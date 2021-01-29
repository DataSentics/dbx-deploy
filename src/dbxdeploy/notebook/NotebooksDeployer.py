from pathlib import PurePosixPath
from typing import List
from requests.exceptions import HTTPError
from databricks_api import DatabricksAPI
from dbxdeploy.dbc.DbcCreator import DbcCreator
from dbxdeploy.dbc.DbcUploader import DbcUploader
from dbxdeploy.notebook.CurrentDirectoryUpdater import CurrentDirectoryUpdater
from dbxdeploy.notebook.Notebook import Notebook
from dbxdeploy.package.PackageMetadata import PackageMetadata
from logging import Logger
from dbxdeploy.deploy.TargetPathsResolver import TargetPathsResolver

class NotebooksDeployer:

    def __init__(
        self,
        workspaceBaseDir: PurePosixPath,
        logger: Logger,
        dbxApi: DatabricksAPI,
        dbcCreator: DbcCreator,
        dbcUploader: DbcUploader,
        currentDirectoryUpdater: CurrentDirectoryUpdater,
        targetPathsResolver: TargetPathsResolver,
    ):
        self.__workspaceBaseDir = workspaceBaseDir
        self.__logger = logger
        self.__dbxApi = dbxApi
        self.__dbcCreator = dbcCreator
        self.__dbcUploader = dbcUploader
        self.__currentDirectoryUpdater = currentDirectoryUpdater
        self.__targetPathsResolver = targetPathsResolver

    def deploy(self, packageMetadata: PackageMetadata, notebooks: List[Notebook]):
        packagePath = self.__targetPathsResolver.getPackageUploadPathForDeploy(packageMetadata)

        self.__logger.info(f'All packages released, updating {self.__workspaceBaseDir}')
        self.__currentDirectoryUpdater.update(notebooks, self.__workspaceBaseDir, packagePath)

    def release(self, packageMetadata: PackageMetadata, notebooks: List[Notebook]):
        self.__logger.info('Building notebooks package (DBC)')
        dbcContent = self.__dbcCreator.create(notebooks, self.__targetPathsResolver.getPackageUploadPathForRelease(packageMetadata))

        _currentPath = self.__targetPathsResolver.getWorkspaceCurrentPath(packageMetadata) # pylint: disable = invalid-name
        releasePath = self.__targetPathsResolver.getWorkspaceReleasePath(packageMetadata)

        self.__logger.info(f'Uploading notebooks package to {releasePath}')
        self.__dbcUploader.upload(dbcContent, releasePath)

        self.__logger.info(f'Cleaning up {_currentPath} if exists')

        try:
            self.__dbxApi.workspace.delete(str(_currentPath), recursive=True)
        except HTTPError as e:
            if e.response.status_code != 404:
                raise

        self.__logger.info(f'Uploading notebooks package to {_currentPath}')
        self.__dbcUploader.upload(dbcContent, _currentPath)
