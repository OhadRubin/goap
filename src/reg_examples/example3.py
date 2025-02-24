from src.goap import AutomatonController, RegAction, RegSensor, RegGoal
from pathlib import Path
import fire


class DirectoryStateSensor(RegSensor):
    binding = "tmp_dir_state"

    def exec(self):
        tmp_path = Path("/tmp/goap_tmp")
        out = "exist" if tmp_path.exists() else "not_exist"
        return out


class TokenStateSensor(RegSensor):
    binding = "tmp_dir_content"

    def exec(self):
        token_path = Path("/tmp/goap_tmp") / ".token"
        out = "token_found" if token_path.exists() else "token_not_found"
        return out


class CreateTmpDir(RegAction):
    effects = {"tmp_dir_state": "exist"}
    preconditions = {"tmp_dir_state": "not_exist"}

    def exec(self):
        Path("/tmp/goap_tmp").mkdir(parents=True, exist_ok=True)


class CreateToken(RegAction):
    effects = {"tmp_dir_content": "token_found"}
    preconditions = {"tmp_dir_state": "exist", "tmp_dir_content": "token_not_found"}

    def exec(self):
        (Path("/tmp/goap_tmp") / ".token").touch()


class Relax(RegAction):
    effects = {"is_relaxed": True}
    preconditions = {"is_relaxed": False}

    def exec(self):
        pass


class CreateTokenGoal(RegGoal):
    desired_state = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}
    priority = 1

class RelaxGoal(RegGoal):
    preconditions = {"tmp_dir_state": "exist", "tmp_dir_content": "token_found"}
    desired_state = {"is_relaxed": True}
    priority = 2


def start():
    reset()
    world_state_matrix = {
        "tmp_dir_state": "not_exist",
        "tmp_dir_content": "token_not_found",
        "is_relaxed": False,
    }
    dir_handler = AutomatonController(
        name="directory_watcher",
        actions=[CreateTmpDir(), CreateToken(), Relax()],
        sensors=[DirectoryStateSensor(), TokenStateSensor()],
        world_state=world_state_matrix,
        
        possible_goals=[CreateTokenGoal(),RelaxGoal()],
    )
    dir_handler.start()


def reset():
    try:
        Path("/tmp/goap_tmp/.token").unlink()
        Path("/tmp/goap_tmp").rmdir()
    except FileNotFoundError:
        pass


# usage: python -m reg_examples.example3 start
if __name__ == "__main__":
    fire.Fire({"start": start, "reset": reset})
