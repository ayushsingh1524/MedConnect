import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchInteractions = createAsyncThunk('interactions/fetchAll', async (filters = {}) => {
  // Construct query string from filters (e.g., ?hcp_id=1)
  const queryParams = new URLSearchParams(filters).toString();
  const url = `/api/v1/interactions${queryParams ? `?${queryParams}` : ''}`;
  
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch interactions');
  return response.json();
});

export const createInteraction = createAsyncThunk('interactions/create', async (interactionData) => {
  const response = await fetch('/api/v1/interactions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(interactionData),
  });
  if (!response.ok) throw new Error('Failed to log interaction');
  return response.json();
});

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Fetch All
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Create
      .addCase(createInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.list.unshift(action.payload); // Add new interaction to top of list
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export default interactionSlice.reducer;
