import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

// We will import the slices and API later as we build them.
// import { baseApi } from './api';

export const store = configureStore({
  reducer: {
    // [baseApi.reducerPath]: baseApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware(),
    // .concat(baseApi.middleware),
});

setupListeners(store.dispatch);
