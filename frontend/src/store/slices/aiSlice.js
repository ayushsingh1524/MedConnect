import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  chatHistory: [],
  isStreaming: false,
  streamedText: '',
  error: null,
};

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    },
    setStreaming: (state, action) => {
      state.isStreaming = action.payload;
      if (action.payload) {
        state.streamedText = '';
      }
    },
    appendStreamText: (state, action) => {
      state.streamedText += action.payload;
    },
    commitStreamedMessage: (state) => {
      if (state.streamedText) {
        state.chatHistory.push({
          role: 'assistant',
          content: state.streamedText,
        });
        state.streamedText = '';
      }
      state.isStreaming = false;
    },
    clearChat: (state) => {
      state.chatHistory = [];
      state.streamedText = '';
      state.isStreaming = false;
      state.error = null;
    },
  },
});

export const { 
  addMessage, 
  setStreaming, 
  appendStreamText, 
  commitStreamedMessage, 
  clearChat 
} = aiSlice.actions;

export default aiSlice.reducer;
