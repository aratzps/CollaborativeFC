import sys
import time

def main():
    print("Starting OCP Sidecar...", flush=True)
    # Simulate startup
    time.sleep(1)
    print("OCP Sidecar Ready.", flush=True)
    
    # Keep alive loop (simulating service)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping OCP Sidecar...", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    main()
