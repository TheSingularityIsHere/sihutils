import datetime
import glob
import zoneinfo

from IPython import display as disp
from matplotlib import pyplot as plt
import pandas as pd
import pynvml

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
