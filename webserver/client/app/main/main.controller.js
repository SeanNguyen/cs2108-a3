'use strict';

var app = angular.module('webserverApp');

app.controller('MainCtrl', MainCtrl);

function MainCtrl($scope, $http, localStorageService, $state, Photo, FileUploader) {
  	$scope.username;
    $scope.uploadImageId;
    $scope.uploader = new FileUploader();
    $scope.uploading = false;

  	active();
  	
  	//implementations
  	function active() {
  		$scope.username = localStorageService.get("username");
  		if(!$scope.username) {
  			$state.go("welcome");
  		}

        $scope.uploader.url = "api/upload";
        $scope.uploader.alias = "image";
        $scope.uploader.formData = [{username: $scope.username}];
        $scope.uploader.autoUpload = true;
        $scope.uploader.removeAfterUpload = true;
        $scope.uploader.onSuccessItem = onUploadSuccessful;
        $scope.uploader.onBeforeUploadItem = onBeforeUpload;
  	}

    function onBeforeUpload (item) {
        $scope.uploading = true;
    }

    function onUploadSuccessful(item, response, status, headers) {
         $scope.uploading = false;
         console.log(response);
    }

};