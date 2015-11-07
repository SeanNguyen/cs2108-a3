'use strict';

angular.module('webserverApp')
  .config(function ($stateProvider) {
    $stateProvider
      .state('photo', {
        url: '/photo/:id',
        templateUrl: 'app/photo/photo.html',
        controller: 'PhotoCtrl'
      });
  });