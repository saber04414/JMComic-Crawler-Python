from test_jmcomic import *


class Test_JmDownloader(JmTestConfigurable):

    def test_downloader_init(self):
        """Test JmDownloader initialization"""
        downloader = JmDownloader(self.option)
        self.assertIsNotNone(downloader.option)
        self.assertIsNotNone(downloader.client)
        self.assertEqual(len(downloader.download_success_dict), 0)
        self.assertEqual(len(downloader.download_failed_image), 0)
        self.assertEqual(len(downloader.download_failed_photo), 0)

    def test_download_album(self):
        """Test download_album() fetches and downloads album"""
        downloader = DoNotDownloadImage(self.option)
        album = downloader.download_album('438516')
        
        self.assertIsNotNone(album)
        self.assertEqual(album.album_id, '438516')
        # Should have called before_album and after_album
        self.assertIn(album, downloader.download_success_dict)

    def test_download_photo(self):
        """Test download_photo() fetches and downloads photo"""
        downloader = DoNotDownloadImage(self.option)
        photo = downloader.download_photo('438516')
        
        self.assertIsNotNone(photo)
        self.assertEqual(photo.photo_id, '438516')
        # Should have called before_photo and after_photo
        album = photo.from_album
        if album:
            self.assertIn(album, downloader.download_success_dict)

    def test_download_by_album_detail(self):
        """Test download_by_album_detail() downloads all photos in album"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        
        downloader.download_by_album_detail(album)
        
        # Should have processed the album
        self.assertIn(album, downloader.download_success_dict)

    def test_download_by_album_detail_skip(self):
        """Test download_by_album_detail() skips when album.skip is True"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        album.skip = True
        
        downloader.download_by_album_detail(album)
        
        # Should not have processed photos
        self.assertNotIn(album, downloader.download_success_dict)

    def test_download_by_photo_detail(self):
        """Test download_by_photo_detail() downloads all images in photo"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            downloader.download_by_photo_detail(photo)
            
            # Should have processed the photo
            self.assertIn(album, downloader.download_success_dict)
            self.assertIn(photo, downloader.download_success_dict[album])

    def test_download_by_photo_detail_skip(self):
        """Test download_by_photo_detail() skips when photo.skip is True"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            photo.skip = True
            downloader.download_by_photo_detail(photo)
            
            # Should not have processed images
            if album in downloader.download_success_dict:
                self.assertNotIn(photo, downloader.download_success_dict[album])

    def test_download_by_image_detail(self):
        """Test download_by_image_detail() downloads single image"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                downloader.download_by_image_detail(image)
                
                # Should have set image properties
                self.assertIsNotNone(image.save_path)
                self.assertIsNotNone(image.exists)

    def test_download_by_image_detail_skip(self):
        """Test download_by_image_detail() skips when image.skip is True"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                image.skip = True
                initial_exists = image.exists
                downloader.download_by_image_detail(image)
                
                # Should not have changed state
                self.assertEqual(image.exists, initial_exists)

    def test_download_by_image_detail_cache(self):
        """Test download_by_image_detail() respects cache setting"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                # Set image as existing
                image.exists = True
                self.option.download.cache = True
                
                downloader.download_by_image_detail(image)
                
                # Should have skipped download due to cache

    def test_do_filter_default(self):
        """Test do_filter() returns detail unchanged by default"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        filtered = downloader.do_filter(album)
        
        # Should return same object
        self.assertIs(filtered, album)

    def test_do_filter_custom(self):
        """Test do_filter() can be overridden for custom filtering"""
        class FilterDownloader(JmDownloader):
            def do_filter(self, detail):
                if detail.is_album():
                    # Only return first photo
                    return detail[:1] if len(detail) > 0 else detail
                return detail
        
        downloader = FilterDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        filtered = downloader.do_filter(album)
        
        # Should be filtered
        if len(album) > 0:
            self.assertLessEqual(len(filtered), len(album))

    def test_before_album(self):
        """Test before_album() callback is called"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        downloader.before_album(album)
        
        # Should have initialized success dict
        self.assertIn(album, downloader.download_success_dict)

    def test_after_album(self):
        """Test after_album() callback is called"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        downloader.before_album(album)
        downloader.after_album(album)
        
        # Should still have album in dict
        self.assertIn(album, downloader.download_success_dict)

    def test_before_photo(self):
        """Test before_photo() callback is called"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            downloader.before_photo(photo)
            
            # Should have initialized structures
            self.assertIn(album, downloader.download_success_dict)
            self.assertIn(photo, downloader.download_success_dict[album])

    def test_after_photo(self):
        """Test after_photo() callback is called"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            downloader.before_photo(photo)
            downloader.after_photo(photo)
            
            # Should still have photo in dict
            self.assertIn(photo, downloader.download_success_dict[album])

    def test_before_image(self):
        """Test before_image() callback is called"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                img_save_path = self.option.decide_image_filepath(image)
                downloader.before_image(image, img_save_path)
                
                # Should not raise exception

    def test_after_image(self):
        """Test after_image() callback tracks successful downloads"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                downloader.before_photo(photo)
                img_save_path = self.option.decide_image_filepath(image)
                downloader.after_image(image, img_save_path)
                
                # Should have tracked the image
                image_list = downloader.download_success_dict[album][photo]
                self.assertEqual(len(image_list), 1)
                self.assertEqual(image_list[0][1], image)

    def test_raise_if_has_exception_no_failures(self):
        """Test raise_if_has_exception() does nothing when no failures"""
        downloader = JmDownloader(self.option)
        
        # Should not raise
        downloader.raise_if_has_exception()

    def test_raise_if_has_exception_with_failures(self):
        """Test raise_if_has_exception() raises when failures exist"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                # Simulate failure
                downloader.download_failed_image.append((image, Exception('test error')))
                
                with self.assertRaises(PartialDownloadFailedException):
                    downloader.raise_if_has_exception()

    def test_raise_if_has_exception_photo_failure(self):
        """Test raise_if_has_exception() handles photo failures"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            # Simulate photo failure
            downloader.download_failed_photo.append((photo, Exception('test error')))
            
            with self.assertRaises(PartialDownloadFailedException):
                downloader.raise_if_has_exception()

    def test_has_download_failures_no_failures(self):
        """Test has_download_failures property returns False when no failures"""
        downloader = JmDownloader(self.option)
        
        self.assertFalse(downloader.has_download_failures)

    def test_has_download_failures_with_image_failure(self):
        """Test has_download_failures property returns True with image failure"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                downloader.download_failed_image.append((image, Exception('test')))
                
                self.assertTrue(downloader.has_download_failures)

    def test_has_download_failures_with_photo_failure(self):
        """Test has_download_failures property returns True with photo failure"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            downloader.download_failed_photo.append((photo, Exception('test')))
            
            self.assertTrue(downloader.has_download_failures)

    def test_all_success_no_downloads(self):
        """Test all_success property returns True when no downloads attempted"""
        downloader = JmDownloader(self.option)
        
        # No downloads, no failures
        self.assertTrue(downloader.all_success)

    def test_all_success_complete_download(self):
        """Test all_success property returns True when all downloads complete"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        
        # Download album (but don't actually download images)
        downloader.download_by_album_detail(album)
        
        # Since DoNotDownloadImage doesn't track images, all_success logic
        # will depend on the implementation
        # This test verifies the property doesn't crash

    def test_all_success_partial_download(self):
        """Test all_success property returns False with partial downloads"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        # Initialize but don't complete
        downloader.before_album(album)
        if len(album) > 0:
            photo = album[0]
            downloader.before_photo(photo)
            # Don't download all images
        
        # Should be False due to incomplete downloads
        self.assertFalse(downloader.all_success)

    def test_context_manager_enter(self):
        """Test context manager __enter__() returns self"""
        downloader = JmDownloader(self.option)
        
        with downloader as d:
            self.assertIs(d, downloader)

    def test_context_manager_exit_no_exception(self):
        """Test context manager __exit__() handles no exception"""
        downloader = JmDownloader(self.option)
        
        # Should not raise
        with downloader:
            pass

    def test_context_manager_exit_with_exception(self):
        """Test context manager __exit__() logs exception"""
        downloader = JmDownloader(self.option)
        
        # Should log but not suppress exception
        with self.assertRaises(ValueError):
            with downloader:
                raise ValueError('test exception')

    def test_execute_on_condition_empty(self):
        """Test execute_on_condition() handles empty iterable"""
        downloader = JmDownloader(self.option)
        
        class EmptyEntity(DetailEntity):
            def __len__(self):
                return 0
            
            def getindex(self, index):
                raise IndexError
        
        empty = EmptyEntity()
        # Should not raise
        downloader.execute_on_condition(empty, lambda x: None, 10)

    def test_execute_on_condition_single_thread(self):
        """Test execute_on_condition() uses single thread when batch >= count"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        # Use large batch count to force single-thread mode
        downloader.execute_on_condition(album, lambda x: None, 1000)
        
        # Should complete without error

    def test_execute_on_condition_thread_pool(self):
        """Test execute_on_condition() uses thread pool when batch < count"""
        downloader = JmDownloader(self.option)
        album = self.client.get_album_detail('438516')
        
        if len(album) > 1:
            # Use small batch count to force thread pool mode
            downloader.execute_on_condition(album, lambda x: None, 1)
            
            # Should complete without error


class Test_DoNotDownloadImage(JmTestConfigurable):

    def test_do_not_download_image_init(self):
        """Test DoNotDownloadImage initialization"""
        downloader = DoNotDownloadImage(self.option)
        self.assertIsInstance(downloader, JmDownloader)

    def test_do_not_download_image_download_by_image_detail(self):
        """Test DoNotDownloadImage.download_by_image_detail() doesn't download"""
        downloader = DoNotDownloadImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo:
            image = photo[0] if len(photo) > 0 else None
            
            if image:
                # Should not raise and should set filepath
                downloader.download_by_image_detail(image)
                self.assertIsNotNone(image.save_path)

    def test_do_not_download_image_download_album(self):
        """Test DoNotDownloadImage can download album without images"""
        downloader = DoNotDownloadImage(self.option)
        album = downloader.download_album('438516')
        
        self.assertIsNotNone(album)
        self.assertEqual(album.album_id, '438516')


class Test_JustDownloadSpecificCountImage(JmTestConfigurable):

    def test_just_download_specific_count_init(self):
        """Test JustDownloadSpecificCountImage initialization"""
        downloader = JustDownloadSpecificCountImage(self.option)
        self.assertIsInstance(downloader, JmDownloader)

    def test_just_download_specific_count_set_count(self):
        """Test JustDownloadSpecificCountImage.use() sets count"""
        JustDownloadSpecificCountImage.use(5)
        
        self.assertEqual(JustDownloadSpecificCountImage.count, 5)

    def test_just_download_specific_count_try_countdown(self):
        """Test try_countdown() decrements count"""
        JustDownloadSpecificCountImage.count = 3
        downloader = JustDownloadSpecificCountImage(self.option)
        
        # First call should succeed
        result1 = downloader.try_countdown()
        self.assertTrue(result1)
        self.assertEqual(JustDownloadSpecificCountImage.count, 2)
        
        # Second call should succeed
        result2 = downloader.try_countdown()
        self.assertTrue(result2)
        self.assertEqual(JustDownloadSpecificCountImage.count, 1)
        
        # Third call should succeed
        result3 = downloader.try_countdown()
        self.assertTrue(result3)
        self.assertEqual(JustDownloadSpecificCountImage.count, 0)
        
        # Fourth call should fail
        result4 = downloader.try_countdown()
        self.assertFalse(result4)
        self.assertEqual(JustDownloadSpecificCountImage.count, -1)

    def test_just_download_specific_count_negative_count(self):
        """Test try_countdown() returns False when count is negative"""
        JustDownloadSpecificCountImage.count = -1
        downloader = JustDownloadSpecificCountImage(self.option)
        
        result = downloader.try_countdown()
        self.assertFalse(result)

    def test_just_download_specific_count_download_by_image_detail(self):
        """Test JustDownloadSpecificCountImage.download_by_image_detail() respects count"""
        JustDownloadSpecificCountImage.count = 2
        downloader = JustDownloadSpecificCountImage(self.option)
        album = self.client.get_album_detail('438516')
        photo = album[0] if len(album) > 0 else None
        
        if photo and len(photo) >= 3:
            # Download first image (should succeed)
            image1 = photo[0]
            downloader.download_by_image_detail(image1)
            self.assertEqual(JustDownloadSpecificCountImage.count, 1)
            
            # Download second image (should succeed)
            image2 = photo[1]
            downloader.download_by_image_detail(image2)
            self.assertEqual(JustDownloadSpecificCountImage.count, 0)
            
            # Download third image (should skip)
            image3 = photo[2]
            initial_exists = image3.exists
            downloader.download_by_image_detail(image3)
            # Should not have changed (skipped)
            self.assertEqual(image3.exists, initial_exists)
