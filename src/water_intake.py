class UserProfile:
    def __init__(self, weight, activity_level, climate):
        """
        Initialize user profile with weight, activity level, and climate.
        :param weight: User's weight in kilograms.
        :param activity_level: User's activity level ('low', 'medium', 'high').
        :param climate: User's climate ('temperate', 'hot', 'very hot').
        """
        self.weight = weight
        self.activity_level = activity_level
        self.climate = climate
        self.water_goal = self.calculate_water_goal()


#Calculate daily water intake goal based on weight, activity level, and climate and returns daily water goal in liters.
    def calculate_water_goal(self):
        
        # Base water intake (30-35 ml per kg of body weight)
        base_water = self.weight * 0.033  # liters per kilogram

        # Adjust for activity level
        if self.activity_level == 'high':
            base_water += 0.5
        elif self.activity_level == 'medium':
            base_water += 0.25

        # Adjust for climate
        if self.climate == 'hot':
            base_water += 0.5
        elif self.climate == 'very hot':
            base_water += 1.0

        return base_water


# Intialize water intake tracket with user profile.
class WaterIntakeTracker:
    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.current_intake = 0



    # Log water or other beverage intake.
    def log_intake(self, amount, beverage_type='water'):
        # Hydration values for different beverages
        hydration_factors = {
            'water': 1.0,
            'tea': 0.8,
            'coffee': 0.7,
            'soda': 0.6,
            'juice': 0.9
        }

        if beverage_type in hydration_factors:
            self.current_intake += amount * hydration_factors[beverage_type]
        else:
            print(f"Unknown beverage type: {beverage_type}")


    # Get progress towards water goal.
    def get_progress(self):
        return self.current_intake / self.user_profile.water_goal

    # Get remaining water intake needed to reach the goal and returns remaining water intake in liters.
    def get_remaining_intake(self):
        return max(0, self.user_profile.water_goal - self.current_intake)