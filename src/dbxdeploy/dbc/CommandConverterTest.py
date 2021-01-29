import unittest
from pyfonycore.bootstrap import bootstrappedContainer
from dbxdeploy.dbc.CommandConverter import CommandConverter

class CommandConverterTest(unittest.TestCase):

    def setUp(self):
        container = bootstrappedContainer.init('test')

        self.__commandConverter = container.get(CommandConverter) # type: CommandConverter

    def test_pythonCode(self):
        self.__testCommand(
            'print("Hello world")',
            'print("Hello world")',
        )

    def test_pythonCode_multiLine_withTitle(self):
        self.__testCommand(
            'print("Hello world")\n\na = 5',
            '# DBTITLE 1,My Command Title\nprint("Hello world")\n\na = 5',
            showCommandTitle=True,
            commandTitle='My Command Title',
        )

    def test_magic(self):
        self.__testCommand(
            '%sql SELECT * FROM test_table',
            '# MAGIC %sql SELECT * FROM test_table'
        )

    def test_magic_multiLine_withTitle(self):
        self.__testCommand(
            '%sql\n\nSELECT * FROM test_table',
            '# DBTITLE 1,My Command Title\n# MAGIC %sql\n# MAGIC \n# MAGIC SELECT * FROM test_table',
            showCommandTitle=True,
            commandTitle='My Command Title',
        )

    def test_installMasterPackageWhl(self):
        self.__testCommand(
            '%pip install /dbfs/FileStore/jars/myproject/2020-03-21_08-56-14_fhpxgwblvi/myproject-1.0-py3-none-any.whl',
            '# MAGIC %installMasterPackageWhl'
        )

    def test_installMasterPackageWhl_withTitle(self):
        self.__testCommand(
            '%pip install /dbfs/FileStore/jars/myproject/2020-03-21_08-56-14_fhpxgwblvi/myproject-1.0-py3-none-any.whl',
            '# DBTITLE 0,My Command Title\n# MAGIC %installMasterPackageWhl',
            showCommandTitle=False,
            commandTitle='My Command Title',
        )

    def __testCommand(self, commandCode: str, expectedLine: str, **kwargs):
        command = {**{'command': commandCode, 'position': 1, 'commandTitle': ''}, **kwargs}

        result = self.__commandConverter.convert(command)

        self.assertEqual(result, expectedLine)

if __name__ == '__main__':
    unittest.main()
