import { Assistant } from "./assistant";
import { AuthWrapper } from "./auth-wrapper";

export default function Home() {
  return (
    <AuthWrapper>
      <Assistant />
    </AuthWrapper>
  );
}
