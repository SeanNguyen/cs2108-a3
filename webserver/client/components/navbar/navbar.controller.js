'use strict';

var app = angular.module('webserverApp');
app.controller('NavbarCtrl', NavbarCtrl);

function NavbarCtrl($scope, localStorageService, $state) {
    $scope.username;
    $scope.signOut = signOut;
    
    active();
    
    //implementations
    function active() {
        $scope.username = localStorageService.get("username");
    }

    function signOut() {
        localStorageService.remove("username");
        $state.go("welcome");
    }
};