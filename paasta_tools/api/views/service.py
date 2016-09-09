#!/usr/bin/env python
# Copyright 2015-2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
PaaSTA service list (instances) etc.
"""
from pyramid.view import view_config

from paasta_tools.api import settings
from paasta_tools.generate_deployments_for_service import get_instance_config_for_service
from paasta_tools.utils import DEFAULT_SOA_DIR
from paasta_tools.utils import list_all_instances_for_service


@view_config(route_name='service.list', request_method='GET', renderer='json')
def list_instances(request):
    service = request.swagger_data.get('service')
    deploy_group = request.swagger_data.get('deploy_group', False)
    if deploy_group:
        instances = [config.get_instance() for config in list(get_instance_config_for_service(DEFAULT_SOA_DIR, service))
                     if config.get_deploy_group() == deploy_group]
    else:
        instances = list_all_instances_for_service(service, clusters=[settings.cluster])
    return {'instances': list(instances)}
