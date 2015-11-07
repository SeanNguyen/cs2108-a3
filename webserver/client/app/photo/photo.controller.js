'use strict';

var app = angular.module('webserverApp');

app.controller('PhotoCtrl', PhotoCtrl);

function PhotoCtrl($scope, localStorageService, $state, Photo, $stateParams) {
    $scope.photo;
    $scope.infoChanged;
    $scope.saving;
    
    $scope.save = save;
    $scope.setDirty = setDirty;
    

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
        })
        .catch(function(err) {
            $scope.photo = null;
        });

        $scope.infoChanged = false;
        $scope.saving = false;
    }

    function save () {
        $scope.saving = true;
        $scope.photo.$update()
        .then(function(res) {
            $scope.infoChanged = false;
            $scope.saving = false;
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
}