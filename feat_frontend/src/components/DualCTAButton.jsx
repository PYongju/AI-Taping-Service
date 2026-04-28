export default function DualCTAButton({
	primaryLabel,
	secondaryLabel,
	onPrimary,
	onSecondary,
	primaryDisabled = false,
	secondaryDisabled = false,
}) {
	return (
		<div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
			<button
				className="btn btn-primary"
				onClick={onPrimary}
				disabled={primaryDisabled}
			>
				{primaryLabel}
			</button>
			<button
				className="btn btn-secondary"
				onClick={onSecondary}
				disabled={secondaryDisabled}
			>
				{secondaryLabel}
			</button>
		</div>
	);
}
