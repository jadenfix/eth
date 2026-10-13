import type { NextApiRequest, NextApiResponse } from 'next';

export default function gatewayDocumentation(_request: NextApiRequest, response: NextApiResponse) {
  response.redirect(307, '/api-gateway');
}
