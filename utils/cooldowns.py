import time

class Cooldown:
    def __init__(self, cooldown_duration: int):
        self.cooldown_duration = cooldown_duration
        self.user_last_interaction = {}
    
    def is_on_cooldown(self, user_id: int) -> bool:
        if user_id in self.user_last_interaction:
            last_time = self.user_last_interaction[user_id]
            current_time = time.time()
            time_diff = current_time - last_time
            return time_diff < self.cooldown_duration
        return False
    
    def get_time_remaining(self, user_id: int) -> float:
        if user_id in self.user_last_interaction:
            last_time = self.user_last_interaction[user_id]
            current_time = time.time()
            time_diff = current_time - last_time
            return max(0, self.cooldown_duration - time_diff)
        return 0
    
    def set_last_interaction(self, user_id: int):
        self.user_last_interaction[user_id] = time.time()
    
    def get_remaining_time_message(self, user_id: int) -> str:
        remaining_time = self.get_time_remaining(user_id)
        if remaining_time > 0:
            return f"Hey! You're on cooldown, Please wait {remaining_time:.1f} seconds."
        return "You are not on cooldown anymore!"
