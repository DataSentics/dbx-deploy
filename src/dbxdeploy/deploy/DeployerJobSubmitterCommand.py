import asyncio
import sys
from logging import Logger
from argparse import Namespace, ArgumentParser
from pathlib import PurePosixPath
from dbxdeploy.deploy.DeployerJobSubmitter import DeployerJobSubmitter
from dbxdeploy.notebook.ConverterResolver import ConverterResolver
from consolebundle.ConsoleCommand import ConsoleCommand

class DeployerJobSubmitterCommand(ConsoleCommand):

    def __init__(
        self,
        logger: Logger,
        converterResolver: ConverterResolver,
        deployerJobSubmitter: DeployerJobSubmitter,
    ):
        self.__logger = logger
        self.__converterResolver = converterResolver
        self.__deployerJobSubmitter = deployerJobSubmitter

    def configure(self, argumentParser: ArgumentParser):
        argumentParser.add_argument(dest='notebookPath', help='Jupyter notebook path relative to project root')

    def getCommand(self) -> str:
        return 'dbx:deploy-submit-job'

    def getDescription(self):
        return 'Deploy to DBX and submit selected notebook as job'

    def run(self, inputArgs: Namespace):
        jupyterNotebookPath = PurePosixPath(inputArgs.notebookPath)

        if self.__converterResolver.isSupported(jupyterNotebookPath) is False:
            formatsDescription = ', '.join(self.__converterResolver.getSupportedFormatsDescriptions())
            self.__logger.error('Only {} can be submitted as Databricks job'.format(formatsDescription))
            sys.exit(1)

        notebookPath = jupyterNotebookPath.relative_to('src').with_suffix('')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__deployerJobSubmitter.deployAndSubmitJob(notebookPath))
