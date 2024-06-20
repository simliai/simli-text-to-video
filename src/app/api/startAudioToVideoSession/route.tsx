import { NextApiRequest, NextApiResponse } from "next";
import { NextRequest, NextResponse } from "next/server";

export const POST = async (req: NextRequest, res: NextResponse) => {
  try {
    
    const metadata = {
        faceId: "9f3a3361-41b4-4157-87e6-9e6e4557ca7f",
        isJPG: true,
        apiKey: process.env.NEXT_PUBLIC_SIMLI_KEY,
        syncAudio: true,
      };
    
      const response = await fetch(
        'https://api.simli.ai/startAudioToVideoSession',
        {
          method: 'POST',
          body: JSON.stringify(metadata),
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    return NextResponse.json(await response.json());
  } catch (error) {
    return NextResponse.json({ error: "Error" }, { status: 400 });
  }
};
