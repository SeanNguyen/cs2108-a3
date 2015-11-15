'use strict';

angular.module('webserverApp')
  .config(function ($stateProvider) {
    $stateProvider
      .state('tag', {
        url: '/tag/:tag',
        templateUrl: 'app/tag/tag.html',
        controller: 'TagController'
      });
  });