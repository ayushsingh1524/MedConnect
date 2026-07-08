import { configureStore } from '@reduxjs/toolkit';
import hcpReducer from './slices/hcpSlice';
import interactionReducer from './slices/interactionSlice';
import aiReducer from './slices/aiSlice';

const store = configureStore({
  reducer: {
    hcps: hcpReducer,
    interactions: interactionReducer,
    ai: aiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export { store };
