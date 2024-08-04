import os

def venv_activate():
    try:
        venv_path = "E:\\vs_code_work_files\\test_venv\\venv\\Scripts\\activate"
        command = f"cmd /k {venv_path}"
        os.system(command)
    except Exception as e:
        print(f"Error activating virtual environment: {e}")

def venv_deactivate():
    try:
        command = "cmd /k deactivate"
        os.system(command)
    except Exception as e:
        print(f"Error deactivating virtual environment: {e}")

def run_server():
    try:
        project_path = "E:\\vs_code_work_files\\matchmaking_assignment\\app\\"
        command = f"cd {project_path} && uvicorn main:app --reload"
        os.system(command)
    except Exception as e:
        print(f"Error running the server: {e}")

try:
    venv_activate()
    run_server()
finally:
    venv_deactivate()