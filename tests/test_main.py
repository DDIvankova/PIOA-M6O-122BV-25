import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMain(unittest.TestCase):
    """Тесты для модуля __main__.py"""
    
    @patch('src.db.__main__.run')
    def test_main_calls_run(self, mock_run):
        """Тест: функция main вызывает run()"""
        from src.db.__main__ import main
        main()
        mock_run.assert_called_once()
    
    @patch('src.db.__main__.run')
    def test_main_calls_run_only_once(self, mock_run):
        """Тест: main вызывает run() только один раз"""
        from src.db.__main__ import main
        main()
        self.assertEqual(mock_run.call_count, 1)
    
    def test_module_has_main_function(self):
        """Тест: модуль содержит функцию main"""
        import src.db.__main__ as main_module
        self.assertTrue(hasattr(main_module, 'main'))
        self.assertTrue(callable(main_module.main))
    
    def test_module_has_run_import(self):
        """Тест: модуль импортирует run из tui"""
        import src.db.__main__ as main_module
        self.assertTrue(hasattr(main_module, 'run'))
    
    @patch('src.db.__main__.run')
    def test_main_executes_without_errors(self, mock_run):
        """Тест: main выполняется без ошибок"""
        from src.db.__main__ import main
        try:
            main()
        except Exception as e:
            self.fail(f"main() вызвал исключение: {e}")
    def test_main_script_direct(self):
        """Прямой тест для __main__.py"""
        import src.db.__main__
        self.assertTrue(True)

import src.db.__main__

if __name__ == '__main__':
    unittest.main()