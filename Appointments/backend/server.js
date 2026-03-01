import express from 'express';
import authRoutes from './routes/auth.js';
import appointmentRoutes from './routes/appointments.js';

const app = express();
app.use(express.json());

app.use('/auth', authRoutes);
app.use('/appointments', appointmentRoutes);

app.listen(process.env.PORT || 3000, () =>
  console.log('Server running')
);