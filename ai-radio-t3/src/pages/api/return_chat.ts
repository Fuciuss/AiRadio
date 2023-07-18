

import { NextApiRequest, NextApiResponse } from 'next'

export default function handler(req: NextApiRequest, res: NextApiResponse) {

    // console.log(req.body)

    const messages = req.body

    console.log(messages)

    // res.status(200).json({ name: 'John Doe' })
    res.status(200).json({ messages: messages })
  }
