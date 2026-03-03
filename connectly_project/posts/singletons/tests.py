from django.test import TestCase
from .config_manager import ConfigManager

class ConfigManagerTestCase(TestCase):

    def setUp(self):
        # Reset the singleton for each test to ensure isolation
        ConfigManager._instance = None
        self.config1 = ConfigManager()
        self.config2 = ConfigManager()

    def test_singleton_instance(self):
        # Both instances should be the same
        self.assertIs(self.config1, self.config2)

    def test_settings_persistence(self):
        # Settings changed in one instance are reflected in the other
        self.config1.set_setting("DEFAULT_PAGE_SIZE", 50)
        self.assertEqual(self.config2.get_setting("DEFAULT_PAGE_SIZE"), 50)

    def test_default_settings(self):
        # Check that default settings exist
        self.assertEqual(self.config1.get_setting("RATE_LIMIT"), 100)
        self.assertTrue(self.config1.get_setting("ENABLE_ANALYTICS"))

    def test_new_setting(self):
        # Adding a new setting works
        self.config1.set_setting("NEW_FEATURE_ENABLED", True)
        self.assertTrue(self.config2.get_setting("NEW_FEATURE_ENABLED"))

    def test_nonexistent_setting(self):
        # Getting a nonexistent key returns None
        self.assertIsNone(self.config1.get_setting("NON_EXISTENT_KEY"))