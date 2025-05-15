local apiHost = std.extVar('apiHost');
local adminHost = std.extVar('adminHost');

{
  apiVersion: 'traefik.io/v1alpha1',
  kind: 'IngressRoute',
  metadata: {
    name: 'data-catalog-backend',
    namespace: 'developer-portal',
  },
  spec: {
    entryPoints: ['websecure'],
    routes: [{
      kind: 'Rule',
      match: 'Host(`' + apiHost + '`) && PathPrefix(`/catalog`) && !PathPrefix(`/catalog/admin`)',
      services: [{
        kind: 'Service',
        name: 'data-catalog-backend',
        port: 80,
      }],
      middlewares: [
          {
            name: 'stripprefix-catalog',
            namespace: 'developer-portal',
          },
          {
            name: 'traefikmiddleware-cors@kubernetescrd'
          },
      ],
    },
    {
      kind: 'Rule',
      match: 'Host(`' + adminHost + '`) && PathPrefix(`/catalog`)',
      services: [{
        kind: 'Service',
        name: 'data-catalog-backend',
        port: 81,
      }],
      middlewares: [
          {
            name: 'stripprefix-catalog',
            namespace: 'developer-portal',
          },
          {
            name: 'traefikmiddleware-cors@kubernetescrd'
          }
      ],
    },
    {
      kind: 'Rule',
      match: 'Host(`' + adminHost + '`) && (PathPrefix(`/catalog/docs`) || PathPrefix(`/catalog/openapi.json`))',
      services: [{
        kind: 'Service',
        name: 'data-catalog-backend',
        port: 81,
      }],
      middlewares: [
          {
            name: 'oauth2-proxy'
          },
          {
            name: 'stripprefix-catalog',
            namespace: 'developer-portal',
          },
          {
            name: 'traefikmiddleware-cors@kubernetescrd'
          }
      ],
    },
    ],
  },
}