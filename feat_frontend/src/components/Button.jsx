import "./Button.css";

export default function Button({
	children,
	variant = "primary",
	disabled = false,
	onClick,
	className = "",
	style,
	...props
}) {
	const cls = ["btn", `btn-${variant}`, className].filter(Boolean).join(" ");
	return (
		<button
			className={cls}
			disabled={disabled}
			onClick={onClick}
			style={style}
			{...props}
		>
			{children}
		</button>
	);
}
