'use strict';

var app = angular.module('webserverApp');

app.controller('PhotoCtrl', PhotoCtrl);

function PhotoCtrl($scope, localStorageService, $state, Photo, $stateParams, $q) {
    $scope.readonly;
    $scope.photo = { tags: []};
    $scope.infoChanged;
    $scope.saving;
    $scope.suggestTags;
    
    $scope.save = save;
    $scope.setDirty = setDirty;
    $scope.onTagAppend = onTagAppend;
    

    active();

    function active() {
        //if the url doesn't have any id with it
        var photoId = -1;
        if($stateParams.id) {
            var photoId = $stateParams.id;
        }

        Photo.get({id: photoId}).$promise
        .then(function(res) {
            $scope.photo = res;

            //get local user
            var localUser = localStorageService.get('username');
            if(!localUser || localUser !== $scope.photo.user) {
               $scope.readonly = true; 
            }

            //if there is no tag on the photo, then suggest some tags
            if(!$scope.photo.tags || $scope.photo.tags.length === 0) {
                getSuggestedTags($scope.photo.path)
                .then(function(tags) {
                    $scope.photo.tags = tags;
                    $scope.suggestTags = true;
                    setDirty();
                })
                .catch(function(err) {
                    console.log("Fail to get result from search engine");
                })
            }
        })
        .catch(function(err) {
            $scope.photo = null;
        });

        $scope.infoChanged = false;
        $scope.saving = false;
        $scope.suggestTags = false;
    }

    function save () {
        $scope.saving = true;
        $scope.photo.$update()
        .then(function(res) {
            $scope.infoChanged = false;
            $scope.saving = false;
            $scope.suggestTags = false;
            reportTagResult($scope.photo.path, $scope.photo.tags);
        })
        .catch(function(err) {
            $scope.saving = false;
            alert("Cannot save changes");
        });
    }

    function setDirty() {
        if(!$scope.saving) {
            $scope.infoChanged = true;
        }
    }

    function onTagAppend(tag) {
        setDirty();
        return tag;
    }

    function getSuggestedTags (imagePath) {
        //call search engine
        var defer = $q.defer();

        defer.resolve(["cat", "dog", "fish"]);

        return defer.promise;
    }

    function reportTagResult(imagePath, tags) {
        //call engine
    }
}