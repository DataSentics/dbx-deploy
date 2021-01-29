# pylint: disable = too-many-instance-attributes
from logging import Logger
from pathlib import Path
from dbxdeploy.cluster.ClusterRestarter import ClusterRestarter
from dbxdeploy.deploy.CurrentAndReleaseDeployer import CurrentAndReleaseDeployer
from dbxdeploy.job.JobsCreatorAndRunner import JobsCreatorAndRunner
from dbxdeploy.job.JobsDeleter import JobsDeleter
from dbxdeploy.notebook.Notebook import Notebook
from dbxdeploy.notebook.NotebooksLocator import NotebooksLocator
from dbxdeploy.package.PackageMetadataLoader import PackageMetadataLoader
from dbxdeploy.package.PackageDeployer import PackageDeployer
import asyncio
from dbxdeploy.deploy.TargetPathsResolver import TargetPathsResolver

class Releaser:

    def __init__(
        self,
        projectBaseDir: Path,
        logger: Logger,
        targetPathsResolver: TargetPathsResolver,
        packageMetadataLoader: PackageMetadataLoader,
        currentAndReleaseDeployer: CurrentAndReleaseDeployer,
        packageDeployer: PackageDeployer,
        clusterRestarter: ClusterRestarter,
        jobsDeleter: JobsDeleter,
        jobsCreatorAndRunner: JobsCreatorAndRunner,
        notebooksLocator: NotebooksLocator,
    ):
        self.__projectBaseDir = projectBaseDir
        self.__logger = logger
        self.__targetPathsResolver = targetPathsResolver
        self.__packageMetadataLoader = packageMetadataLoader
        self.__currentAndReleaseDeployer = currentAndReleaseDeployer
        self.__packageDeployer = packageDeployer
        self.__clusterRestarter = clusterRestarter
        self.__jobsDeleter = jobsDeleter
        self.__jobsCreatorAndRunner = jobsCreatorAndRunner
        self.__notebooksLocator = notebooksLocator

    async def release(self):
        packageMetadata = self.__packageMetadataLoader.load(self.__projectBaseDir)

        loop = asyncio.get_event_loop()

        packageReleaseFuture = loop.run_in_executor(None, self.__packageDeployer.release, packageMetadata)
        dbcDeployFuture = loop.run_in_executor(None, self.__currentAndReleaseDeployer.release, packageMetadata)

        await packageReleaseFuture
        await dbcDeployFuture

        self.__logger.info('--')

        consumerNotebooks = self.__notebooksLocator.locateConsumers()

        if consumerNotebooks:
            self.__clusterRestarter.restart()

            def createJobNotebookPath(consumerNotebook: Notebook):
                return str(self.__targetPathsResolver.getWorkspaceReleasePath(packageMetadata) / consumerNotebook.databricksRelativePath)

            consumerNotebooksReleasePaths = set(map(createJobNotebookPath, consumerNotebooks))

            self.__jobsDeleter.remove(consumerNotebooksReleasePaths)

            self.__logger.info('--')

            self.__jobsCreatorAndRunner.createAndRun(consumerNotebooks, packageMetadata)

        self.__logger.info('Deployment completed')
