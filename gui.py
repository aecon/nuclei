#!/usr/bin/env python3
"""Nuclei Counter — Dash web GUI."""

import glob
import os
import subprocess
import sys
import threading

import dash
from dash import html, dcc, Input, Output, State, callback

from nuclei import nuclei as NucleiProcessor
import skimage.io

# ---------------------------------------------------------------------------
# Global processing state (polled by dcc.Interval)
# ---------------------------------------------------------------------------
_state = {
    'running': False,
    'current': 0,
    'total': 0,
    'current_file': '',
    'done': False,
    'error': None,
}

def _reset_state():
    _state.update(running=False, current=0, total=0, current_file='', done=False, error=None, skipped=0)

# ---------------------------------------------------------------------------
# Processing thread
# ---------------------------------------------------------------------------

def _run_processing(basedir, skip_existing=False):
    try:
        files = sorted(glob.glob(os.path.join(basedir, '**', '*.tif'), recursive=True))
        files = [f for f in files if os.sep + 'labels' + os.sep not in f]

        _state['total'] = len(files)
        if not files:
            _state['error'] = 'No .tif files found in folder.'
            _state['running'] = False
            return

        # build set of CSV files and write fresh headers
        csv_files = set()
        for file in files:
            output_file = os.path.join(
                basedir,
                "counts_" + os.path.dirname(file).split(basedir)[1].replace('/', '_').replace(' ', '') + ".csv",
            )
            if output_file not in csv_files:
                csv_files.add(output_file)
                NucleiProcessor.write_header_static(output_file)

        n = None  # lazy-init model only if needed
        skipped = 0

        for i, file in enumerate(files):
            _state['current'] = i + 1
            _state['current_file'] = os.path.relpath(file, basedir)

            output_file = os.path.join(
                basedir,
                "counts_" + os.path.dirname(file).split(basedir)[1].replace('/', '_').replace(' ', '') + ".csv",
            )
            output_folder = os.path.join(os.path.dirname(file), "labels")
            output_labels = os.path.join(output_folder, os.path.basename(file) + "_labels.tif")

            # try to reuse existing labels from a previous run
            if skip_existing and os.path.exists(output_labels):
                try:
                    labels = skimage.io.imread(output_labels, plugin='tifffile')
                    import numpy as np
                    Nnuclei = len(np.unique(labels)) - 1
                    NucleiProcessor.write_data_static(output_file, file, Nnuclei)
                    skipped += 1
                    continue
                except Exception:
                    pass  # corrupted file, fall through to re-process

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # lazy-load model on first image that needs processing
            if n is None:
                n = NucleiProcessor()

            try:
                img = skimage.io.imread(file, plugin='tifffile')
            except Exception as e:
                print(f"WARNING: Could not read {file}: {e}")
                continue

            Nnuclei, labels = n.process(img)
            n.write_data(output_file, file, Nnuclei)

            skimage.io.imsave(output_labels, labels, plugin='tifffile', check_contrast=False)

        _state['skipped'] = skipped
        _state['done'] = True
    except Exception as e:
        _state['error'] = str(e)
    finally:
        _state['running'] = False

# ---------------------------------------------------------------------------
# Dash app
# ---------------------------------------------------------------------------

app = dash.Dash(__name__, title="Nuclei Counter")

app.layout = html.Div([
    html.H1("Nuclei Counter", style={'textAlign': 'center'}),

    # -- Folder input --
    html.Div([
        html.Label("Plates folder:"),
        dcc.Input(id='folder-input', type='text', placeholder='/path/to/plates',
                  style={'width': '600px', 'marginRight': '10px'}),
        html.Button("Browse", id='btn-browse', n_clicks=0, style={'marginRight': '5px'}),
        html.Button("Run", id='btn-run', n_clicks=0),
    ], style={'margin': '10px'}),

    # -- Skip existing --
    html.Div([
        dcc.Checklist(id='skip-existing', options=[{'label': ' Skip already processed images', 'value': 'skip'}],
                      value=[], inline=True),
    ], style={'margin': '10px'}),

    # -- Output info --
    html.Div(id='output-info', style={'margin': '10px', 'color': '#666', 'fontSize': '14px'}),

    # -- Progress --
    html.Div([
        html.Div(id='progress-bar-container', children=[
            html.Div(id='progress-bar-fill', style={
                'width': '0%', 'height': '24px',
                'backgroundColor': '#4CAF50', 'borderRadius': '4px',
                'transition': 'width 0.3s',
            }),
        ], style={
            'width': '100%', 'backgroundColor': '#e0e0e0', 'borderRadius': '4px',
            'overflow': 'hidden', 'display': 'none',
        }),
        html.Div(id='status-text', style={'margin': '8px 0', 'color': '#333'}),
    ], style={'margin': '10px'}),

    # -- Polling timer --
    dcc.Interval(id='poll-interval', interval=500, disabled=True),
], style={'fontFamily': 'sans-serif', 'maxWidth': '900px', 'margin': '0 auto'})


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

def _browse_folder():
    code = "\n".join([
        "import tkinter as tk",
        "from tkinter import filedialog",
        "root = tk.Tk()",
        "root.withdraw()",
        "root.attributes('-topmost', True)",
        "result = filedialog.askdirectory(title='Select plates folder')",
        "print(result if result else '', end='')",
        "root.destroy()",
    ])
    proc = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    folder = proc.stdout.strip()
    return folder if folder else None


@callback(
    Output('folder-input', 'value'),
    Input('btn-browse', 'n_clicks'),
    prevent_initial_call=True,
)
def browse(n_clicks):
    folder = _browse_folder()
    return folder if folder else dash.no_update


@callback(
    Output('output-info', 'children'),
    Input('folder-input', 'value'),
)
def update_output_info(folder):
    if not folder or not folder.strip():
        return ""
    folder = folder.strip()
    if not os.path.isdir(folder):
        return html.Span("Folder does not exist.", style={'color': 'red'})
    files = glob.glob(os.path.join(folder, '**', '*.tif'), recursive=True)
    files = [f for f in files if os.sep + 'labels' + os.sep not in f]
    return html.Div([
        html.Span(f"Found {len(files)} .tif images."),
        html.Br(),
        html.Span(f"CSV files will be saved in: {folder}"),
        html.Br(),
        html.Span("Label images will be saved in labels/ subfolder next to each image."),
    ])


@callback(
    Output('poll-interval', 'disabled'),
    Output('status-text', 'children', allow_duplicate=True),
    Output('progress-bar-container', 'style', allow_duplicate=True),
    Input('btn-run', 'n_clicks'),
    State('folder-input', 'value'),
    State('skip-existing', 'value'),
    prevent_initial_call=True,
)
def start_run(n_clicks, folder, skip_existing):
    bar_hidden = {'width': '100%', 'backgroundColor': '#e0e0e0', 'borderRadius': '4px',
                  'overflow': 'hidden', 'display': 'none'}
    bar_visible = {**bar_hidden, 'display': 'block'}

    if _state['running']:
        return dash.no_update, "Already running.", dash.no_update
    if not folder or not os.path.isdir(folder.strip()):
        return dash.no_update, "Please select a valid folder.", dash.no_update

    _reset_state()
    _state['running'] = True
    skip = 'skip' in (skip_existing or [])
    threading.Thread(target=_run_processing, args=(folder.strip(), skip), daemon=True).start()
    return False, "Starting...", bar_visible


@callback(
    Output('status-text', 'children'),
    Output('progress-bar-fill', 'style'),
    Output('progress-bar-container', 'style'),
    Output('poll-interval', 'disabled', allow_duplicate=True),
    Input('poll-interval', 'n_intervals'),
    prevent_initial_call=True,
)
def poll_progress(n):
    bar_base = {'height': '24px', 'backgroundColor': '#4CAF50', 'borderRadius': '4px',
                'transition': 'width 0.3s'}
    bar_container_visible = {'width': '100%', 'backgroundColor': '#e0e0e0', 'borderRadius': '4px',
                             'overflow': 'hidden', 'display': 'block'}
    bar_container_hidden = {**bar_container_visible, 'display': 'none'}

    if _state['error']:
        msg = _state['error']
        _reset_state()
        return f"Error: {msg}", {**bar_base, 'width': '0%'}, bar_container_hidden, True

    if _state['done']:
        total = _state['total']
        skipped = _state['skipped']
        _reset_state()
        msg = f"Done! Processed {total - skipped}/{total} images."
        if skipped:
            msg += f" ({skipped} skipped)"
        return msg, {**bar_base, 'width': '100%'}, bar_container_hidden, True

    if not _state['running']:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    current = _state['current']
    total = _state['total']
    pct = (current / total * 100) if total else 0
    fname = _state['current_file']
    status = f"Processing {current}/{total}: {fname}"
    return status, {**bar_base, 'width': f'{pct:.1f}%'}, bar_container_visible, False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import webbrowser
    import argparse
    parser = argparse.ArgumentParser(description="Nuclei Counter GUI")
    parser.add_argument("--port", type=int, default=8051, help="Port (default: 8051)")
    args = parser.parse_args()
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{args.port}")).start()
    app.run(port=args.port)


if __name__ == "__main__":
    main()
