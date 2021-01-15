##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

import logging
import uuid
import io
import gzip
import json

from typing import List, Union, Dict, Optional
from enum import Enum
from azure.quantum.optimization import Term
from azure.quantum.storage import upload_blob, ContainerClient


logger = logging.getLogger(__name__)


__all__ = ['Problem', 'ProblemType']

class ProblemType(str, Enum):
    pubo  = 0
    ising = 1


class Problem:

    def __init__(self, name: str, terms: Optional[List[Term]] = None, init_config :Optional[Dict[str,int]] = None, problem_type: ProblemType = ProblemType.ising):
        self.name = name
        self.terms = terms if terms is not None else []
        self.problem_type = problem_type
        self.init_config = init_config

    def serialize(self) -> str :
        result = { 
            "cost_function": {
                "version": "1.1" if self.init_config else "1.0",
                "type": self.problem_type.name,
                "terms": [term.to_dict() for term in self.terms]
            }       
        }

        if self.init_config : 
            result["cost_function"]["initial_configuration"]= self.init_config

        return json.dumps(result)

    def add_term(self, c: Union[int, float], indices: List[int]) : 
        self.terms.append(Term(indices=indices, c=c))
    
    def add_terms(self, terms: List[Term]) : 
        self.terms = self.terms + terms    

    def upload(self, workspace, container_name:str="qio-problems", blob_name:str=None, compress:bool=True):
        """Uploads an optimization problem instance to the cloud storage linked with the Workspace.

        :param workspace: interaction terms of the problem.
        :return: uri of the uploaded problem
        """
        if blob_name is None:
            blob_name = '{}-{}'.format(self.name, uuid.uuid1())
            
        problem_json = self.serialize()
        logger.debug("Problem json: " + problem_json)
        
        content_type = "application/json"
        encoding = ""
        data = io.BytesIO()
        if compress:
            encoding = "gzip"
            with gzip.GzipFile(fileobj=data, mode='w') as fo:
                fo.write(problem_json.encode())
        else:
            data.write(problem_json.encode())

        if not workspace.storage:
            # No storage account is passed, use the linked one
            container_uri = workspace._get_linked_storage_sas_uri(container_name)
            container_client = ContainerClient.from_container_url(container_uri)
            return upload_blob(container_client, blob_name, content_type, encoding, data.getvalue(), returnSasToken=False)
        else:
            # Use the specified storage account
            container_client = ContainerClient.from_connection_string(workspace.storage, container_name)
            return upload_blob(container_client, blob_name, content_type, encoding, data.getvalue(), returnSasToken=True)
