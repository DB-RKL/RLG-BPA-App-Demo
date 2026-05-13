interface IconProps {
  name: string;
  className?: string;
  fill?: boolean;
  size?: number;
}

export default function Icon({ name, className = "", fill, size }: IconProps) {
  return (
    <span
      className={`material-symbols-outlined ${fill ? "fill" : ""} ${className}`}
      style={size ? { fontSize: size } : undefined}
    >
      {name}
    </span>
  );
}
