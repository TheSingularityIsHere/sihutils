import datetime
import glob
import json
import os
import subprocess
import zoneinfo

from IPython import display as disp
from matplotlib import pyplot as plt
import numy as np
import pandas as pd
import pynvml
from scipy.ndimage import binary_closing


def _plot(df):
  fig, ax1 = plt.subplots(figsize=(12, 6))
  fig.subplots_adjust(right=0.7)

  # Axis 1: GPU Utilization
  p1, = ax1.plot(df['ts'], df['gpu_util'], 'r-', label='Util (%)')
  ax1.set_ylabel('Utilization (%)', color='r')
  ax1.tick_params(axis='y', labelcolor='r')
  ax1.set_ylim(0, 110)

  # Axis 2: VRAM
  ax2 = ax1.twinx()
  p2, = ax2.plot(df['ts'], df['gpu_vram_used_mb'], 'b-', label='VRAM (MB)')
  ax2.set_ylabel('VRAM (MB)', color='b')
  ax2.tick_params(axis='y', labelcolor='b')

  # Axis 3: Number of Files
  ax3 = ax1.twinx()
  ax3.spines['right'].set_position(('outward', 60))
  p3, = ax3.plot(df['ts'], df['num_files'], 'g-', label='Num Files')
  ax3.set_ylabel('Num Files', color='g')
  ax3.tick_params(axis='y', labelcolor='g')

  # Axis 4: Temperature
  ax4 = ax1.twinx()
  ax4.spines['right'].set_position(('outward', 120))
  p4, = ax4.plot(df['ts'], df['gpu_temp'], 'm-', label='Temp (°C)')
  ax4.set_ylabel('Temp (°C)', color='m')
  ax4.tick_params(axis='y', labelcolor='m')

  ax1.set_xlabel('Time')
  ax1.legend(handles=[p1, p2, p3, p4], loc='upper left')
  plt.show()


def _get_row():
  num_files = len(glob.glob('runpod-slim/ComfyUI/output/video/*.mp4'))

  pynvml.nvmlInit()
  handle = pynvml.nvmlDeviceGetHandleByIndex(0)
  info = pynvml.nvmlDeviceGetMemoryInfo(handle)
  vram_used = info.used / 1024**2 # MB
  util = pynvml.nvmlDeviceGetUtilizationRates(handle)
  temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

  return dict(
    num_files=num_files,
    gpu_vram_used_mb=vram_used,
    gpu_util=util.gpu,
    gpu_temp=temp,
    ts=datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Zurich")),
  )


def loop(rows=()):
  rows = list(rows)
  try:
    while True:
      disp.clear_output(wait=True)
      rows.append(_get_row())
      df = pd.DataFrame(rows)
      _plot(df)
      plt.show()
  except KeyboardInterrupt:
    pass
  return rows


def _get_video_metadata(file_path):
  stats = os.stat(file_path)
  size_mb = stats.st_size / (1024 * 1024)
  creation_time = datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

  cmd = [
    'ffprobe', '-v', 'quiet', '-print_format', 'json',
    '-show_streams', '-select_streams', 'v:0', file_path
  ]
  res = subprocess.check_output(cmd).decode('utf-8')
  streams = json.loads(res).get('streams', [{}])[0]

  return {
    'file': os.path.basename(file_path),
    'width': streams.get('width'),
    'height': streams.get('height'),
    'frames': int(streams.get('nb_frames', 0)),
    'size_mb': round(size_mb, 2),
    'created': creation_time
  }



def _get_on_times(rows, threshold=10, gap_tolerance=10):
  df = pd.DataFrame(rows)
  # Create binary mask of 'on' state
  is_on = (df['gpu_util'] > threshold).values

  # Fill gaps caused by oscillations (gap_tolerance is in samples)
  is_on_clean = binary_closing(is_on, structure=np.ones(gap_tolerance))

  # Find transitions
  diff = np.diff(is_on_clean.astype(int))
  starts = np.where(diff == 1)[0] + 1
  ends = np.where(diff == -1)[0] + 1

  # Handle edge cases (starts 'on' or ends 'on')
  if is_on_clean[0]: starts = np.insert(starts, 0, 0)
  if is_on_clean[-1]: ends = np.append(ends, len(df))

  # Combine into intervals
  blocks = []
  for s, e in zip(starts, ends):
    blocks.append({
      'start_ts': df['ts'].iloc[s],
      'end_ts': df['ts'].iloc[min(e, len(df)-1)],
      'duration_sec': (df['ts'].iloc[min(e, len(df)-1)] - df['ts'].iloc[s]).total_seconds()
    })
  return pd.DataFrame(blocks)


def export(rows):
  df = pd.DataFrame(rows)
  df['ts'] = df['ts'].dt.strftime('%Y-%m-%d %H:%M:%S')
  mp4_paths = sorted(glob.glob('runpod-slim/ComfyUI/output/video/*.mp4'))
  csv_text = '\n'.join((
      df.to_csv(index=False),
      _get_on_times(rows).to_csv(index=False),
      pd.DataFrame([_get_video_metadata(f) for f in mp4_paths]).to_csv(index=False),
  )).replace('\n', '\\n').replace("'", "\\'")
  js_code = f"""
  navigator.clipboard.writeText('{csv_text}').then(() => {{
    console.log('CSV copied to local clipboard');
  }});
  """
  disp.display(disp.Javascript(js_code))
  print('1. Paste CSV and save as *public* Gist:')
  print('https://gist.github.com/')
  print()
  print('2. Share link:')
  print('https://figur.li/hitl/')
