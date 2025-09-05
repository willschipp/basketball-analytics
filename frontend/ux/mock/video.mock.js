import { defineMock } from 'vite-plugin-mock-dev-server'

export default [
  defineMock({
    url: '/api/v1/videos',
    method: 'GET',
    // Using a function to dynamically add timestamps each time the mock is called
    body: () => [
      {
        id: 1,
        title: 'Video 1',
        url: '/video-1',
        timestamp: new Date().toISOString(),
      },
      {
        id: 2,
        title: 'Video 2',
        url: '/video-2',
        timestamp: new Date().toISOString(),
      },
    ],
  }),
  defineMock({
    url: '/api/v1/videos/1',
    method: 'GET',
    body: () => {
      return {
        id: 1,
        title: 'Video 1',
        timestamp: new Date().toISOString()        
      }
    }
  })
]