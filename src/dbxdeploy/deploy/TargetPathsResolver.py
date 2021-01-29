from pygit2 import GitError # pylint: disable = no-name-in-module
from pathlib import PurePosixPath
from dbxdeploy.git.CurrentBranchResolver import CurrentBranchResolver
from dbxdeploy.package.PackageMetadata import PackageMetadata

class TargetPathsResolver:

    def __init__(
        self,
        packageDeployPath: str,
        packageReleasePath: str,
        packageCurrentPath: str,
        workspaceReleasePath: str,
        workspaceCurrentPath: str,
        currentBranchResolver: CurrentBranchResolver,
    ):
        self.__packageDeployPath = packageDeployPath
        self.__packageReleasePath = packageReleasePath
        self.__packageCurrentPath = packageCurrentPath
        self.__workspaceReleasePath = PurePosixPath(workspaceReleasePath)
        self.__workspaceCurrentPath = PurePosixPath(workspaceCurrentPath)
        self.__currentBranchResolver = currentBranchResolver

    def getPackageUploadPathForDeploy(self, packageMetadata: PackageMetadata):
        return self.__replacePackagePath(packageMetadata, self.__packageDeployPath)

    def getPackageUploadPathForRelease(self, packageMetadata: PackageMetadata):
        return self.__replacePackagePath(packageMetadata, self.__packageReleasePath)

    def hasPackageUploadPathForCurrent(self):
        return self.__packageCurrentPath is not None

    def getPackageUploadPathForCurrent(self, packageMetadata: PackageMetadata):
        return self.__replacePackagePath(packageMetadata, self.__packageCurrentPath)

    def getWorkspaceReleasePath(self, packageMetadata: PackageMetadata) -> PurePosixPath:
        return self.__replaceWorkspacePath(packageMetadata, self.__workspaceReleasePath)

    def getWorkspaceCurrentPath(self, packageMetadata: PackageMetadata) -> PurePosixPath:
        return self.__replaceWorkspacePath(packageMetadata, self.__workspaceCurrentPath)

    def __replacePackagePath(self, packageMetadata: PackageMetadata, packagePath: str):
        replacements = {
            'packageName': packageMetadata.packageName,
            'packageFilename': packageMetadata.getPackageFilename(),
            'currentTime': packageMetadata.dateTime.strftime('%Y-%m-%d_%H-%M-%S'),
            'randomString': packageMetadata.randomString,
        }

        if '{currentBranch}' in packagePath:
            try:
                replacements['currentBranch'] = self.__currentBranchResolver.resolve()
            except GitError:
                replacements['currentBranch'] = '__no_git_repo__'

        return packagePath.format(**replacements)

    def __replaceWorkspacePath(self, packageMetadata: PackageMetadata, workspacePath: PurePosixPath):
        replacements = {
            'currentTime': packageMetadata.dateTime.strftime('%Y-%m-%d_%H:%M:%S'),
            'randomString': packageMetadata.randomString,
        }

        if '{currentBranch}' in str(workspacePath):
            replacements['currentBranch'] = self.__currentBranchResolver.resolve()

        return PurePosixPath(str(workspacePath).format(**replacements))
