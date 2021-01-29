from dbxdeploy.package.PackageBuilder import PackageBuilder
from dbxdeploy.package.PackageMetadata import PackageMetadata
from pathlib import Path
from logging import Logger
from dbxdeploy.deploy.TargetPathsResolver import TargetPathsResolver
from dbxdeploy.package.PackageUploaderInterface import PackageUploaderInterface

class PackageDeployer:

    def __init__(
        self,
        projectBaseDir: Path,
        logger: Logger,
        packageUploader: PackageUploaderInterface,
        packageBuilder: PackageBuilder,
        targetPathsResolver: TargetPathsResolver,
    ):
        self.__projectBaseDir = projectBaseDir
        self.__logger = logger
        self.__packageUploader = packageUploader
        self.__packageBuilder = packageBuilder
        self.__targetPathsResolver = targetPathsResolver

    def deploy(self, packageMetadata: PackageMetadata):
        whlPath = self.__targetPathsResolver.getPackageUploadPathForDeploy(packageMetadata)

        def whlContentReadyCallback(content):
            self.__upload(content, whlPath)

        self.__invoke(packageMetadata, whlContentReadyCallback)

    def release(self, packageMetadata: PackageMetadata):
        whlPath = self.__targetPathsResolver.getPackageUploadPathForRelease(packageMetadata)

        def whlContentReadyCallback(content):
            self.__upload(content, whlPath)

            if self.__targetPathsResolver.hasPackageUploadPathForCurrent():
                whlCurrentPath = self.__targetPathsResolver.getPackageUploadPathForCurrent(packageMetadata)
                self.__upload(content, whlCurrentPath)

        self.__invoke(packageMetadata, whlContentReadyCallback)

    def __invoke(self, packageMetadata: PackageMetadata, whlContentReadyCallback: callable):
        self.__logger.info('Building master package (WHL)')

        packagePath = self.__packageBuilder.build(self.__projectBaseDir, packageMetadata.getPackageFilename())

        with packagePath.open('rb') as file:
            content = file.read()

            whlContentReadyCallback(content)

        self.__logger.info('App package uploaded')

    def __upload(self, content, whlPath: str):
        self.__logger.info(f'Uploading WHL package to {whlPath}')
        self.__packageUploader.upload(content, whlPath, overwrite=True)
