import express from 'express';
import { pool } from '../db.js';
import jwt from 'jsonwebtoken';

const router = express.Router();

function auth(req, res, next) {
  const header = req.headers.authorization;
  if (!header) return res.sendStatus(401);

  const token = header.split(' ')[1];
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.sendStatus(403);
  }
}

router.post('/', auth, async (req, res) => {
  const { date, description } = req.body;

  await pool.query(
    'INSERT INTO appointments (user_id, date, description) VALUES ($1, $2, $3)',
    [req.user.id, date, description]
  );

  res.json({ message: 'Appointment booked' });
});

router.get('/', auth, async (req, res) => {
  const result = await pool.query(
    'SELECT * FROM appointments WHERE user_id=$1 ORDER BY date',
    [req.user.id]
  );

  res.json(result.rows);
});

export default router;