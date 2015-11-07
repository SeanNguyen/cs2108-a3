'use strict';

var app = angular.module('webserverApp');

app.controller('MainCtrl', MainCtrl);

function MainCtrl($scope, $http, localStorageService, $state, Photo, FileUploader) {
  	$scope.username;
    $scope.uploadImageId;
    $scope.uploader = new FileUploader();
    $scope.uploading;
    $scope.loading;
    $scope.photos;

  	active();
  	
  	//implementations
  	function active() {
        $scope.uploading = false;
        
  		$scope.username = localStorageService.get("username");
  		if(!$scope.username) {
  			$state.go("welcome");
  		}

        //load images of current user
        $scope.loading = true;
        Photo.query({username :$scope.username})
        .$promise.then(function(res) {
            $scope.photos = res;
            $scope.loading = false;
        })
        .catch(function(err) {
            alert("Cannot connect to server");
        });

        //set up uploader
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