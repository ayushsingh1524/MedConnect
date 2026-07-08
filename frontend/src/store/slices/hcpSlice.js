import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunks for API calls
export const fetchHCPs = createAsyncThunk('hcps/fetchAll', async () => {
  const response = await fetch('/api/v1/hcps');
  if (!response.ok) throw new Error('Failed to fetch HCPs');
  return response.json();
});

export const fetchHCPById = createAsyncThunk('hcps/fetchById', async (id) => {
  const response = await fetch(`/api/v1/hcps/${id}`);
  if (!response.ok) throw new Error('Failed to fetch HCP details');
  return response.json();
});

const hcpSlice = createSlice({
  name: 'hcps',
  initialState: {
    list: [],
    currentHCP: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearCurrentHCP: (state) => {
      state.currentHCP = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch All
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.doctors || action.payload;
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Fetch Single
      .addCase(fetchHCPById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHCPById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentHCP = action.payload;
      })
      .addCase(fetchHCPById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearCurrentHCP } = hcpSlice.actions;
export default hcpSlice.reducer;
