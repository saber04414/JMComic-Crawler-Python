from test_jmcomic import *
import tempfile
import os


class Test_JmOption(JmTestConfigurable):

    def test_option_default(self):
        """Test JmOption.default() creates option with default values"""
        option = JmOption.default()
        self.assertIsNotNone(option)
        self.assertIsNotNone(option.dir_rule)
        self.assertIsNotNone(option.download)
        self.assertIsNotNone(option.client)
        self.assertIsNotNone(option.plugins)

    def test_option_construct(self):
        """Test JmOption.construct() with custom dict"""
        custom_dict = {
            'dir_rule': {
                'rule': 'Bd_Aid',
                'base_dir': './test_dir',
            },
            'download': {
                'cache': False,
            }
        }
        option = JmOption.construct(custom_dict)
        self.assertEqual(option.dir_rule.rule_dsl, 'Bd_Aid')
        self.assertIn('test_dir', option.dir_rule.base_dir)
        self.assertEqual(option.download.cache, False)

    def test_option_construct_without_default(self):
        """Test JmOption.construct() with cover_default=False"""
        custom_dict = {
            'dir_rule': {
                'rule': 'Bd_Aid',
                'base_dir': './test_dir',
            }
        }
        option = JmOption.construct(custom_dict, cover_default=False)
        self.assertEqual(option.dir_rule.rule_dsl, 'Bd_Aid')
        # Should not have default download settings
        self.assertFalse(hasattr(option.download, 'cache') or option.download.get('cache') is None)

    def test_option_from_file(self):
        """Test JmOption.from_file() loads from YAML file"""
        # Use existing test option file
        option_file = './assets/option/option_test_api.yml'
        if os.path.exists(option_file):
            option = JmOption.from_file(option_file)
            self.assertIsNotNone(option)
            self.assertEqual(option.filepath, option_file)
            self.assertEqual(option.dir_rule.normalize_zh, 'zh-cn')

    def test_option_from_str(self):
        """Test create_option_by_str() creates option from string"""
        yml_str = '''
dir_rule:
  rule: Bd_Aid
  base_dir: ./test
download:
  cache: true
'''
        option = create_option_by_str(yml_str)
        self.assertIsNotNone(option)
        self.assertEqual(option.dir_rule.rule_dsl, 'Bd_Aid')
        self.assertEqual(option.download.cache, True)

    def test_option_to_file(self):
        """Test option.to_file() saves to file"""
        option = JmOption.default()
        option.filepath = None
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            temp_path = f.name
        
        try:
            option.filepath = temp_path
            option.to_file()
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify it can be loaded back
            loaded_option = JmOption.from_file(temp_path)
            self.assertIsNotNone(loaded_option)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_option_deconstruct(self):
        """Test option.deconstruct() returns proper dict structure"""
        option = JmOption.default()
        dic = option.deconstruct()
        
        self.assertIn('version', dic)
        self.assertIn('dir_rule', dic)
        self.assertIn('download', dic)
        self.assertIn('client', dic)
        self.assertIn('plugins', dic)
        self.assertIn('log', dic)
        
        # Check dir_rule structure
        self.assertIn('rule', dic['dir_rule'])
        self.assertIn('base_dir', dic['dir_rule'])

    def test_option_copy(self):
        """Test option.copy_option() creates independent copy"""
        option = JmOption.default()
        copied = option.copy_option()
        
        self.assertIsNotNone(copied)
        self.assertEqual(copied.dir_rule.rule_dsl, option.dir_rule.rule_dsl)
        # Should be different objects
        self.assertIsNot(copied, option)

    def test_option_merge_default_dict(self):
        """Test merge_default_dict() merges user dict with defaults"""
        user_dict = {
            'download': {
                'cache': False,
            }
        }
        merged = JmOption.merge_default_dict(user_dict)
        
        # Should have user value
        self.assertEqual(merged['download']['cache'], False)
        # Should have default values for other keys
        self.assertIn('dir_rule', merged)
        self.assertIn('client', merged)

    def test_option_update_cookies(self):
        """Test update_cookies() updates client cookies"""
        option = JmOption.default()
        new_cookies = {'test_cookie': 'test_value'}
        
        option.update_cookies(new_cookies)
        
        cookies = option.client.postman.meta_data.cookies
        self.assertIsNotNone(cookies)
        self.assertEqual(cookies.get('test_cookie'), 'test_value')

    def test_option_update_cookies_merge(self):
        """Test update_cookies() merges with existing cookies"""
        option = JmOption.default()
        option.client.postman.meta_data.cookies = {'existing': 'value'}
        
        new_cookies = {'new_cookie': 'new_value'}
        option.update_cookies(new_cookies)
        
        cookies = option.client.postman.meta_data.cookies
        self.assertEqual(cookies.get('existing'), 'value')
        self.assertEqual(cookies.get('new_cookie'), 'new_value')

    def test_option_new_jm_client(self):
        """Test new_jm_client() creates new client instance"""
        option = JmOption.default()
        client1 = option.new_jm_client()
        client2 = option.new_jm_client()
        
        self.assertIsNotNone(client1)
        self.assertIsNotNone(client2)
        # Should be different instances
        self.assertIsNot(client1, client2)

    def test_option_build_jm_client(self):
        """Test build_jm_client() returns cached client"""
        option = JmOption.default()
        client1 = option.build_jm_client()
        client2 = option.build_jm_client()
        
        # Should return same instance (cached)
        self.assertIs(client1, client2)

    def test_option_new_jm_client_with_domain(self):
        """Test new_jm_client() with custom domain"""
        option = JmOption.default()
        custom_domain = ['test.domain.com']
        client = option.new_jm_client(domain_list=custom_domain)
        
        self.assertIsNotNone(client)
        domain_list = client.get_domain_list()
        self.assertIn('test.domain.com', domain_list)

    def test_option_new_jm_client_with_impl(self):
        """Test new_jm_client() with custom implementation"""
        option = JmOption.default()
        client = option.new_jm_client(impl='api')
        
        self.assertIsNotNone(client)
        self.assertEqual(client.client_key, 'api')

    def test_option_compatible_with_old_versions(self):
        """Test compatible_with_old_versions() handles old format"""
        old_dict = {
            'download': {
                'threading': {
                    'batch_count': 10,  # Old format
                }
            },
            'plugin': {  # Old key name
                'after_init': []
            }
        }
        
        # Should not raise exception
        JmOption.compatible_with_old_versions(old_dict)
        
        # Should convert batch_count to image
        self.assertEqual(old_dict['download']['threading']['image'], 10)
        # Should convert plugin to plugins
        self.assertIn('plugins', old_dict)
        self.assertNotIn('plugin', old_dict)

    def test_option_call_all_plugin(self):
        """Test call_all_plugin() invokes plugins"""
        option = JmOption.default()
        
        # Add a test plugin
        test_called = []
        
        class TestPlugin(JmOptionPlugin):
            plugin_key = 'test_plugin'
            
            def invoke(self, **kwargs):
                test_called.append(True)
        
        JmModuleConfig.register_plugin(TestPlugin)
        
        try:
            option.plugins['test_group'] = [{
                'plugin': 'test_plugin',
                'kwargs': {}
            }]
            
            option.call_all_plugin('test_group', safe=True)
            self.assertEqual(len(test_called), 1)
        finally:
            # Cleanup
            if 'test_plugin' in JmModuleConfig.REGISTRY_PLUGIN:
                del JmModuleConfig.REGISTRY_PLUGIN['test_plugin']

    def test_option_invoke_plugin(self):
        """Test invoke_plugin() calls plugin with parameters"""
        option = JmOption.default()
        
        test_kwargs = {}
        
        class TestPlugin(JmOptionPlugin):
            plugin_key = 'test_invoke_plugin'
            
            def invoke(self, **kwargs):
                test_kwargs.update(kwargs)
        
        JmModuleConfig.register_plugin(TestPlugin)
        
        try:
            option.invoke_plugin(
                TestPlugin,
                {'param1': 'value1'},
                {'param2': 'value2'},
                {'plugin': 'test_invoke_plugin'}
            )
            
            # extra should override kwargs
            self.assertEqual(test_kwargs.get('param1'), 'value1')
            self.assertEqual(test_kwargs.get('param2'), 'value2')
        finally:
            if 'test_invoke_plugin' in JmModuleConfig.REGISTRY_PLUGIN:
                del JmModuleConfig.REGISTRY_PLUGIN['test_invoke_plugin']


class Test_DirRule(JmTestConfigurable):

    def test_dir_rule_init(self):
        """Test DirRule initialization"""
        rule = DirRule('Bd_Aid', base_dir='./test')
        self.assertEqual(rule.rule_dsl, 'Bd_Aid')
        self.assertIn('test', rule.base_dir)
        self.assertIsNone(rule.normalize_zh)

    def test_dir_rule_init_with_normalize(self):
        """Test DirRule with normalize_zh"""
        rule = DirRule('Bd_Aid', base_dir='./test', normalize_zh='zh-cn')
        self.assertEqual(rule.normalize_zh, 'zh-cn')

    def test_dir_rule_split_rule_dsl_underscore(self):
        """Test split_rule_dsl() with underscore separator"""
        rule = DirRule('Bd_Aid_Pname', base_dir='./test')
        rule_list = rule.split_rule_dsl('Bd_Aid_Pname')
        self.assertEqual(rule_list, ['Bd', 'Aid', 'Pname'])

    def test_dir_rule_split_rule_dsl_slash(self):
        """Test split_rule_dsl() with slash separator"""
        rule = DirRule('Bd/Aid/Pname', base_dir='./test')
        rule_list = rule.split_rule_dsl('Bd/Aid/Pname')
        self.assertEqual(rule_list, ['Bd', 'Aid', 'Pname'])

    def test_dir_rule_split_rule_dsl_auto_base_dir(self):
        """Test split_rule_dsl() auto-adds base dir"""
        rule = DirRule('Aid_Pname', base_dir='./test')
        rule_list = rule.split_rule_dsl('Aid_Pname')
        self.assertEqual(rule_list[0], 'Bd')

    def test_dir_rule_get_rule_parser_detail_rule(self):
        """Test get_rule_parser() for detail rules (A/P prefix)"""
        parser = DirRule.get_rule_parser('Aid')
        self.assertEqual(parser, DirRule.parse_detail_rule)

    def test_dir_rule_get_rule_parser_f_string(self):
        """Test get_rule_parser() for f-string rules"""
        parser = DirRule.get_rule_parser('{Aid}_{Pname}')
        self.assertEqual(parser, DirRule.parse_f_string_rule)

    def test_dir_rule_parse_bd_rule(self):
        """Test parse_bd_rule() returns base_dir"""
        rule = DirRule('Bd_Aid', base_dir='./test')
        result = rule.parse_bd_rule(None, None, 'Bd')
        self.assertIn('test', result)

    def test_dir_rule_parse_detail_rule_album(self):
        """Test parse_detail_rule() for album fields"""
        album = self.client.get_album_detail('438516')
        result = DirRule.parse_detail_rule(album, None, 'Aid')
        self.assertEqual(result, album.album_id)

    def test_dir_rule_parse_detail_rule_photo(self):
        """Test parse_detail_rule() for photo fields"""
        album = self.client.get_album_detail('438516')
        photo = album[0]
        result = DirRule.parse_detail_rule(album, photo, 'Pname')
        self.assertEqual(result, photo.name)

    def test_dir_rule_parse_f_string_rule(self):
        """Test parse_f_string_rule() formats with properties"""
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            result = DirRule.parse_f_string_rule(album, photo, '{Aid}_{Pname}')
            self.assertIn(album.album_id, result)
            self.assertIn(photo.name, result)

    def test_dir_rule_decide_image_save_dir(self):
        """Test decide_image_save_dir() generates path"""
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            rule = DirRule('Bd_Aid_Pname', base_dir=workspace())
            save_dir = rule.decide_image_save_dir(album, photo)
            self.assertIsNotNone(save_dir)
            self.assertIn(album.album_id, save_dir)

    def test_dir_rule_decide_album_root_dir(self):
        """Test decide_album_root_dir() generates album root path"""
        album = self.client.get_album_detail('438516')
        rule = DirRule('Bd_Aid', base_dir=workspace())
        root_dir = rule.decide_album_root_dir(album)
        self.assertIsNotNone(root_dir)
        self.assertIn(album.album_id, root_dir)

    def test_dir_rule_apply_rule_to_filename(self):
        """Test apply_rule_to_filename() generates filename"""
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            filename = DirRule.apply_rule_to_filename(album, photo, 'Pname')
            self.assertEqual(filename, photo.name)

    def test_dir_rule_with_normalize_zh_cn(self):
        """Test DirRule with zh-cn normalization"""
        # This test would require actual Chinese text
        rule = DirRule('Bd_Aid', base_dir='./test', normalize_zh='zh-cn')
        self.assertEqual(rule.normalize_zh, 'zh-cn')


class Test_CacheRegistry(JmTestConfigurable):

    def test_cache_registry_level_option(self):
        """Test CacheRegistry.level_option() creates option-level cache"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        cache_dict1 = CacheRegistry.level_option(option, client)
        cache_dict2 = CacheRegistry.level_option(option, client)
        
        # Same option should return same cache dict
        self.assertIs(cache_dict1, cache_dict2)

    def test_cache_registry_level_client(self):
        """Test CacheRegistry.level_client() creates client-level cache"""
        option = JmOption.default()
        client1 = option.new_jm_client()
        client2 = option.new_jm_client()
        
        cache_dict1 = CacheRegistry.level_client(option, client1)
        cache_dict2 = CacheRegistry.level_client(option, client2)
        
        # Different clients should return different cache dicts
        self.assertIsNot(cache_dict1, cache_dict2)

    def test_cache_registry_enable_client_cache_none(self):
        """Test enable_client_cache_on_condition() with None"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        CacheRegistry.enable_client_cache_on_condition(option, client, None)
        self.assertIsNone(client.get_cache_dict())

    def test_cache_registry_enable_client_cache_false(self):
        """Test enable_client_cache_on_condition() with False"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        CacheRegistry.enable_client_cache_on_condition(option, client, False)
        self.assertIsNone(client.get_cache_dict())

    def test_cache_registry_enable_client_cache_true(self):
        """Test enable_client_cache_on_condition() with True"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        CacheRegistry.enable_client_cache_on_condition(option, client, True)
        cache_dict = client.get_cache_dict()
        self.assertIsNotNone(cache_dict)

    def test_cache_registry_enable_client_cache_string(self):
        """Test enable_client_cache_on_condition() with string"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        CacheRegistry.enable_client_cache_on_condition(option, client, 'level_option')
        cache_dict = client.get_cache_dict()
        self.assertIsNotNone(cache_dict)

    def test_cache_registry_enable_client_cache_invalid_string(self):
        """Test enable_client_cache_on_condition() with invalid string raises"""
        option = JmOption.default()
        client = option.new_jm_client()
        
        with self.assertRaises(JmcomicException):
            CacheRegistry.enable_client_cache_on_condition(option, client, 'invalid_cache_level')

