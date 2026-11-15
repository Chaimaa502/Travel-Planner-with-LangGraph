import unittest

from travel_planner.workflow import create_travel_plan


class TravelPlannerWorkflowTests(unittest.TestCase):
    def test_plan_contains_all_specialist_outputs(self):
        plan = create_travel_plan("Plan a 4 day trip from Paris to Rome")

        self.assertEqual(plan.origin, "Paris")
        self.assertEqual(plan.destination, "Rome")
        self.assertEqual(plan.trip_length_days, 4)
        self.assertEqual(len(plan.flights), 1)
        self.assertEqual(len(plan.hotels), 2)
        self.assertEqual(len(plan.itinerary), 4)

    def test_default_duration_is_three_days(self):
        plan = create_travel_plan("I want to visit Tokyo from London")

        self.assertEqual(plan.trip_length_days, 3)
        self.assertEqual([day.day for day in plan.itinerary], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()

