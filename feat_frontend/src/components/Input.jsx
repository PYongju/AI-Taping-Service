import "./Input.css";

export default function Input({
	type = "text",
	placeholder = "",
	value,
	onChange,
	onFocus,
	onBlur,
	disabled = false,
	error = false,
	helperText = "",
	className = "",
	...props
}) {
	const inputClass = ["input", error && "input-error", className]
		.filter(Boolean)
		.join(" ");

	return (
		<div className="input-wrapper">
			<input
				type={type}
				placeholder={placeholder}
				value={value}
				onChange={onChange}
				onFocus={onFocus}
				onBlur={onBlur}
				disabled={disabled}
				className={inputClass}
				{...props}
			/>
			{helperText && (
				<span
					className={`input-helper ${error ? "input-helper-error" : ""}`}
				>
					{helperText}
				</span>
			)}
		</div>
	);
}
