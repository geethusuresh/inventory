'use strict';

/* Services */

// Demonstrate how to register services
// In this case it is a simple value service.
var stock_serv = angular.module('smartbook.services', ['ngResource']);

stock_serv.value('version', '0.1');

stock_serv.factory('share', function()
{
    return {
        messages : {
            show : false,
            type : '',
            message : ''
        },
        loader : {
            show : false
        }
    };
});