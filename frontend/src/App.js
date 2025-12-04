import React, { useState, useEffect } from 'react';
import { fetchContestData } from './services/api';
import { CONTEST, MESSAGES, APP } from './constants';
import './App.css';

function App() {
  const [contestType, setContestType] = useState(CONTEST.TYPES.WEEKLY);
  const [contestNo, setContestNo] = useState('');
  const [channelNo, setChannelNo] = useState('');
  const [username, setUsername] = useState('');
  const [results, setResults] = useState(null);
  const [obtained, setObtained] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [loadingActualRatings, setLoadingActualRatings] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState(APP.DEFAULT_THEME);

  // Load theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  // Toggle theme function
  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setObtained(null);

    try {
      console.log(contestType, contestNo, channelNo, username);
      const { predictions, actualRatings, error } = await fetchContestData(
        {
          contestType,
          contestNo,
          channelNo,
          username
        },
        {
          onPredictionsStart: () => setLoadingPredictions(true),
          onPredictionsEnd: () => setLoadingPredictions(false),
          onActualRatingsStart: () => setLoadingActualRatings(true),
          onActualRatingsEnd: () => setLoadingActualRatings(false)
        }
      );

      if (error) {
        throw error;
      }
      console.log(predictions);
      console.log(actualRatings);
      setResults(predictions);
      setObtained(actualRatings);

    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setContestNo('');
    setChannelNo('');
    setUsername('');
    setResults(null);
    setObtained(null);
    setError(null);
  };

  return (
    <div>
      {/* Theme Toggle Button */}
      <button
        className="theme-toggle"
        onClick={toggleTheme}
        aria-label="Toggle theme"
        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      >
        {theme === 'dark' ? '☀' : '🌙'}
      </button>

      <header className="sketch-border mb-8">
        <h1>
          <i className="fas fa-terminal header-icon"></i>
          Rating Predictions
        </h1>
      </header>

      <main>
        {/* <div className="flex gap-4 mb-8 w-full">
          <button id="btnLeft" type="button" className="active-button" aria-label="Leetcode rating predictions button">
            &gt; leetcode_rating_predictions.exe
          </button>
        </div> */}
        <section id="contentSection" className="w-full">
          <form id="ratingForm" onSubmit={handleSubmit}>
            <div id="radioButtons">
              <label>
                <input
                  type="radio"
                  name="contestType"
                  value={CONTEST.TYPES.WEEKLY}
                  checked={contestType === CONTEST.TYPES.WEEKLY}
                  onChange={(e) => setContestType(e.target.value)}
                />
                <span>weekly</span>
              </label>
              <label>
                <input
                  type="radio"
                  name="contestType"
                  value={CONTEST.TYPES.BIWEEKLY}
                  checked={contestType === CONTEST.TYPES.BIWEEKLY}
                  onChange={(e) => setContestType(e.target.value)}
                />
                <span>biweekly</span>
              </label>
            </div>
            <input
              type="text"
              placeholder="contest_no"
              aria-label="Contest number"
              name="contestNo"
              value={contestNo}
              onChange={(e) => setContestNo(e.target.value)}
              required
              title="contest no."
            />
            <input
              type="text"
              placeholder="channel_no"
              aria-label="Channel number"
              name="channelNo"
              title="discord channel number"
              value={channelNo}
              onChange={(e) => setChannelNo(e.target.value)}
            />
            <span className="or-text">-- OR --</span>
            <input
              type="text"
              placeholder="username"
              aria-label="Username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <button type="submit" aria-label="Submit">
              [ENTER]
            </button>
            <button type="button" id="clearRedirectBtn" aria-label="Clear and Reset" onClick={handleClear}>
              [CLEAR]
            </button>
          </form>

          <h1 id="title" className="contest-title">
            {results?.contestName ? (
              <p className="contest-name">{results.contestName}</p>
            ) : (
              <>
                {MESSAGES.STATUS.READY}
                {results?.status && ` ${results.status}`}
              </>
            )}
          </h1>
          <div className="user-grid">
            {loading && (
              <div className="loading-status">
                <p className="status-message">{MESSAGES.LOADING.INITIALIZING}</p>
                {loadingPredictions && <p className="status-detail">{MESSAGES.LOADING.PREDICTIONS}</p>}
                {loadingActualRatings && <p className="status-detail">{MESSAGES.LOADING.ACTUAL_RATINGS}</p>}
              </div>
            )}
            {error && <p className="error-message">ERROR: {error}</p>}

            {!loading && !error && results?.users && results.users.length > 0 && (
              results.users.map((user, index) => (
                <div className="user-card" key={index}>
                  <span className="username">
                    {user.link ? (
                      <>
                        <a href={user.link}>{user.username}</a>{user.error ? (
                          <>
                            : <code>{obtained[user.username]?.rating !== undefined ? obtained[user.username]?.rating.toFixed(2) : obtained[user.username]?.rating}</code>
                          </>) : (<></>)
                        }
                      </>
                    ) : (
                      user.username
                    )}
                  </span>
                  <ul>
                    {user.error ? (
                      <li className="not-participated">{user.error}</li>
                    ) : user.attended ? (
                      <>
                        <li>RANK: <code>{user.rank}</code></li>
                        <li>OLD_RATING: <code>{user?.old_rating?.toFixed(2)}</code></li>
                        {obtained && obtained[user.username] && !obtained[user.username]?.error ? (
                          <div>
                            <li>NEW_RATING: <strike><code>{user?.new_rating?.toFixed(2)}</code></strike> <code>{obtained[user.username]?.rating !== undefined ? obtained[user.username]?.rating.toFixed(2) : obtained[user.username]?.rating}</code></li>
                          </div>
                        ) : (
                          <li>PREDICTED_RATING: <code>{user?.new_rating?.toFixed(2)}</code></li>
                        )}
                        <li>
                          {user.delta_rating < 0 ? (
                            <>DELTA: <code>{user.delta_rating?.toFixed(2)}</code></>
                          ) : (
                            <>DELTA: <code>+{user.delta_rating?.toFixed(2)}</code></>
                          )}
                        </li>
                        <li>ATTENDED: <code>{user.attendedContestsCount}</code></li>
                      </>
                    ) : (
                      <li className="not-participated">{user.error || "DID NOT PARTICIPATE"}</li>
                    )}
                  </ul>
                </div>
              ))
            )}

            {!loading && !error && results?.users && results.users.length === 0 && (
              <div className="user-card">
                <p className="status-message">{MESSAGES.STATUS.NO_DATA}</p>
              </div>
            )}

            {!loading && !error && !results && (
              <p className="status-message">{MESSAGES.STATUS.AWAITING}</p>
            )}
          </div>
        </section>
      </main>

      <footer>
        <p>COPYRIGHT (C) 2025 RATING PREDICTIONS SYSTEM</p>
      </footer>
    </div>
  );
}

export default App;
