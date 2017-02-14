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
from __future__ import absolute_import
from __future__ import unicode_literals

import contextlib

import mock
from pytest import raises

from paasta_tools import long_running_service_tools
from paasta_tools.utils import InvalidInstanceConfig
from paasta_tools.utils import compose_job_id


class TestLongRunningServiceConfig(object):

    def test_get_healthcheck_cmd_happy(self):
        fake_conf = long_running_service_tools.LongRunningServiceConfig(
            service='fake_name',
            cluster='fake_cluster',
            instance='fake_instance',
            config_dict={'healthcheck_cmd': 'test_cmd'},
            branch_dict={},
        )
        actual = fake_conf.get_healthcheck_cmd()
        assert actual == 'test_cmd'

    def test_get_healthcheck_cmd_raises_when_unset(self):
        fake_conf = long_running_service_tools.LongRunningServiceConfig(
            service='fake_name',
            cluster='fake_cluster',
            instance='fake_instance',
            config_dict={},
            branch_dict={},
        )
        with raises(InvalidInstanceConfig) as exc:
            fake_conf.get_healthcheck_cmd()
        assert "healthcheck mode 'cmd' requires a healthcheck_cmd to run" in str(exc.value)

    def test_get_healthcheck_for_instance_http(self):
        fake_service = 'fake_service'
        fake_namespace = 'fake_namespace'
        fake_hostname = 'fake_hostname'
        fake_random_port = 666

        fake_path = '/fake_path'
        fake_service_config = long_running_service_tools.LongRunningServiceConfig(
            service=fake_service,
            cluster='fake_cluster',
            instance=fake_namespace,
            config_dict={},
            branch_dict={},
        )
        fake_service_namespace_config = long_running_service_tools.ServiceNamespaceConfig({
            'mode': 'http',
            'healthcheck_uri': fake_path,
        })
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True,
                       return_value=fake_service_namespace_config),
            mock.patch('socket.getfqdn', autospec=True, return_value=fake_hostname),
        ) as (
            load_service_namespace_config_patch,
            hostname_patch
        ):
            expected = ('http', 'http://%s:%d%s' % (fake_hostname, fake_random_port, fake_path))
            actual = long_running_service_tools.get_healthcheck_for_instance(
                fake_service, fake_namespace, fake_service_config, fake_random_port)
            assert expected == actual

    def test_get_healthcheck_for_instance_tcp(self):
        fake_service = 'fake_service'
        fake_namespace = 'fake_namespace'
        fake_hostname = 'fake_hostname'
        fake_random_port = 666

        fake_service_config = long_running_service_tools.LongRunningServiceConfig(
            service=fake_service,
            cluster='fake_cluster',
            instance=fake_namespace,
            config_dict={},
            branch_dict={},
        )
        fake_service_namespace_config = long_running_service_tools.ServiceNamespaceConfig({
            'mode': 'tcp',
        })
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True,
                       return_value=fake_service_namespace_config),
            mock.patch('socket.getfqdn', autospec=True, return_value=fake_hostname),
        ) as (
            load_service_namespace_config_patch,
            hostname_patch
        ):
            expected = ('tcp', 'tcp://%s:%d' % (fake_hostname, fake_random_port))
            actual = long_running_service_tools.get_healthcheck_for_instance(
                fake_service, fake_namespace, fake_service_config, fake_random_port)
            assert expected == actual

    def test_get_healthcheck_for_instance_cmd(self):
        fake_service = 'fake_service'
        fake_namespace = 'fake_namespace'
        fake_hostname = 'fake_hostname'
        fake_random_port = 666
        fake_cmd = '/bin/fake_command'
        fake_service_config = long_running_service_tools.LongRunningServiceConfig(
            service=fake_service,
            cluster='fake_cluster',
            instance=fake_namespace,
            config_dict={
                'instances': 1,
                'healthcheck_mode': 'cmd',
                'healthcheck_cmd': fake_cmd
            },
            branch_dict={},
        )
        fake_service_namespace_config = long_running_service_tools.ServiceNamespaceConfig({})
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True,
                       return_value=fake_service_namespace_config),
            mock.patch('socket.getfqdn', autospec=True, return_value=fake_hostname),
        ) as (
            load_service_namespace_config_patch,
            hostname_patch
        ):
            expected = ('cmd', fake_cmd)
            actual = long_running_service_tools.get_healthcheck_for_instance(
                fake_service, fake_namespace, fake_service_config, fake_random_port)
            assert expected == actual

    def test_get_healthcheck_for_instance_other(self):
        fake_service = 'fake_service'
        fake_namespace = 'fake_namespace'
        fake_hostname = 'fake_hostname'
        fake_random_port = 666
        fake_service_config = long_running_service_tools.LongRunningServiceConfig(
            service=fake_service,
            cluster='fake_cluster',
            instance=fake_namespace,
            config_dict={
                'healthcheck_mode': None,
            },
            branch_dict={},
        )
        fake_service_namespace_config = long_running_service_tools.ServiceNamespaceConfig({})
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True,
                       return_value=fake_service_namespace_config),
            mock.patch('socket.getfqdn', autospec=True, return_value=fake_hostname),
        ) as (
            load_service_namespace_config_patch,
            hostname_patch
        ):
            expected = (None, None)
            actual = long_running_service_tools.get_healthcheck_for_instance(
                fake_service, fake_namespace, fake_service_config, fake_random_port)
            assert expected == actual

    def test_get_healthcheck_for_instance_custom_soadir(self):
        fake_service = 'fake_service'
        fake_namespace = 'fake_namespace'
        fake_hostname = 'fake_hostname'
        fake_random_port = 666
        fake_soadir = '/fake/soadir'
        fake_service_config = long_running_service_tools.LongRunningServiceConfig(
            service=fake_service,
            cluster='fake_cluster',
            instance=fake_namespace,
            config_dict={
                'healthcheck_mode': None,
            },
            branch_dict={},
        )
        fake_service_namespace_config = long_running_service_tools.ServiceNamespaceConfig({})
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True,
                       return_value=fake_service_namespace_config),
            mock.patch('socket.getfqdn', autospec=True, return_value=fake_hostname),
        ) as (
            load_service_namespace_config_patch,
            hostname_patch
        ):
            expected = (None, None)
            actual = long_running_service_tools.get_healthcheck_for_instance(
                fake_service, fake_namespace, fake_service_config, fake_random_port, soa_dir=fake_soadir)
            assert expected == actual
            load_service_namespace_config_patch.assert_called_once_with(fake_service, fake_namespace, fake_soadir)

    def test_get_instances_in_config(self):
        fake_conf = long_running_service_tools.LongRunningServiceConfig(
            service='fake_name',
            cluster='fake_cluster',
            instance='fake_instance',
            config_dict={'instances': -10},
            branch_dict={'desired_state': 'start'},
        )
        assert fake_conf.get_instances() == -10

    def test_get_instances_default(self):
        fake_conf = long_running_service_tools.LongRunningServiceConfig(
            service='fake_name',
            cluster='fake_cluster',
            instance='fake_instance',
            config_dict={},
            branch_dict={},
        )
        assert fake_conf.get_instances() == 1

    def test_get_instances_respects_false(self):
        fake_conf = long_running_service_tools.LongRunningServiceConfig(
            service='fake_name',
            cluster='fake_cluster',
            instance='fake_instance',
            config_dict={'instances': False},
            branch_dict={'desired_state': 'start'},
        )
        assert fake_conf.get_instances() == 0

    def test_get_registrations_has_value(self):
        name = 'dont_worry'
        instance = 'im_a_professional'
        cluster = 'andromeda'
        namespaces = ['spacename', 'spaceiscool', 'rocketsarecooler']
        registrations = [compose_job_id(name, ns) for ns in namespaces]
        job_config = long_running_service_tools.LongRunningServiceConfig(
            service=name,
            cluster=cluster,
            instance=instance,
            config_dict={'registrations': registrations},
            branch_dict={},
        )
        actual_registrations = job_config.get_registrations()
        assert set(actual_registrations) == set(registrations)

    def test_read_proxy_port(self):
        name = 'thats_no_moon'
        instance = 'thats_a_space_station'
        cluster = 'shot_line'
        soa_dir = 'drink_up'
        namespace = 'thirsty_mock'
        fake_port = 1234567890
        fake_nerve = long_running_service_tools.ServiceNamespaceConfig({'proxy_port': fake_port})
        job_config = long_running_service_tools.LongRunningServiceConfig(
            name, cluster, instance,
            {"registrations": [compose_job_id(name, namespace)]},
            {},
        )
        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True, return_value=fake_nerve)
        ) as (
            read_config_patch,
        ):
            actual = job_config.read_proxy_port(soa_dir=soa_dir)
            assert fake_port == actual
            read_config_patch.assert_called_once_with(name, namespace, soa_dir)

    def test_get_proxy_port_for_instance_defaults_to_none(self):
        name = 'thats_no_moon'
        instance = 'thats_a_space_station'
        cluster = 'shot_line'
        soa_dir = 'drink_up'
        namespace = 'thirsty_mock'
        expected = None
        job_config = long_running_service_tools.LongRunningServiceConfig(
            name, cluster, instance,
            {"registrations": [compose_job_id(name, namespace)]},
            {},
        )

        with contextlib.nested(
            mock.patch('paasta_tools.long_running_service_tools.load_service_namespace_config',
                       autospec=True, return_value={})
        ) as (
            read_config_patch,
        ):
            actual = job_config.read_proxy_port(soa_dir=soa_dir)
            assert expected == actual
            read_config_patch.assert_called_once_with(name, namespace, soa_dir)


class TestServiceNamespaceConfig(object):

    def test_get_mode_default(self):
        assert long_running_service_tools.ServiceNamespaceConfig().get_mode() is None

    def test_get_mode_default_when_port_specified(self):
        config = {'proxy_port': 1234}
        assert long_running_service_tools.ServiceNamespaceConfig(config).get_mode() == 'http'

    def test_get_mode_valid(self):
        config = {'mode': 'tcp'}
        assert long_running_service_tools.ServiceNamespaceConfig(config).get_mode() == 'tcp'

    def test_get_mode_invalid(self):
        config = {'mode': 'paasta'}
        with raises(long_running_service_tools.InvalidSmartstackMode):
            long_running_service_tools.ServiceNamespaceConfig(config).get_mode()

    def test_get_healthcheck_uri_default(self):
        assert long_running_service_tools.ServiceNamespaceConfig().get_healthcheck_uri() == '/status'

    def test_get_discover_default(self):
        assert long_running_service_tools.ServiceNamespaceConfig().get_discover() == 'region'
