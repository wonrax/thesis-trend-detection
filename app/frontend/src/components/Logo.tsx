import Link from "./Link";
import Text from "./Text";
import { useNavigate } from "react-router-dom";

export const Logo = () => {
  const navigate = useNavigate();
  return (
    <Link href="/" onClick={() => navigate("/")}>
      <Text
        fontSize="xxl"
        fontWeight="medium"
        className="hover:underline cursor-pointer"
      >
        Xu hướng
      </Text>
    </Link>
  );
};

export default Logo;
