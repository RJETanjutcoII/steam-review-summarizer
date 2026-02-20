import './ResultDisplay.css'

function ResultDisplay({ game, appId, summary }) {
  return (
    <div className="result">
      <div className="result__header">
        <h2 className="result__game-name">
          <a
            href={`https://store.steampowered.com/app/${appId}/`}
            target="_blank"
            rel="noopener noreferrer"
          >
            {game}
          </a>
        </h2>

        <img
          className="result__banner"
          src={`https://cdn.akamai.steamstatic.com/steam/apps/${appId}/header.jpg`}
          alt={`${game} banner`}
        />
      </div>

      <div className="result__sections">
        <div className="result__section result__section--positive">
          <h3 className="result__section-title result__section-title--positive">
            Praised
          </h3>
          <ul className="result__list">
            {summary.praised.map((point, index) => (
              <li key={index} className="result__item">
                {point}
              </li>
            ))}
          </ul>
        </div>

        <div className="result__section result__section--negative">
          <h3 className="result__section-title result__section-title--negative">
            Criticized
          </h3>
          <ul className="result__list">
            {summary.criticized.map((point, index) => (
              <li key={index} className="result__item">
                {point}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ResultDisplay
