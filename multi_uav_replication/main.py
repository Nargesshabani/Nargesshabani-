import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/multi_uav_mpl')
import argparse,json
from pathlib import Path
from config import Config
from evaluation import run
from visualization import figures

def main():
    parser=argparse.ArgumentParser(description='Conditional reproduction of Guo et al.; see docs')
    parser.add_argument('--config');parser.add_argument('--output',default=str(Path(__file__).parent))
    args=parser.parse_args();cfg=Config.load(args.config) if args.config else Config()
    print(json.dumps(run(cfg,args.output),indent=2));figures(args.output)
if __name__=='__main__':main()
