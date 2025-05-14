{
  apiVersion: 'traefik.io/v1alpha1',
  kind: 'Middleware',
  metadata: {
    name: 'stripprefix-catalog',
  },
  spec: {
    stripPrefix: {
        prefixes: ['/catalog'],
        forceSlash: true,
    }
  },
}