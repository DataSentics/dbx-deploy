import re

class PackageInstaller:

    def __init__(
        self,
        packageBaseDir: str,
    ):
        self.__packageBaseDir = packageBaseDir

    def getPackageInstallCommand(self, packageFilePath: str):
        return f'%pip install {self.__modifyDbfs(packageFilePath)}'

    def isPackageInstallCommand(self, commandCode: str):
        regExp = '^' + re.escape(f'%pip install {self.__modifyDbfs(self.__packageBaseDir)}') + '.+-py3-none-any.whl$'

        return re.match(regExp, commandCode) is not None

    def __modifyDbfs(self, path: str):
        return '/dbfs/' + path.lstrip('dbfs:/')
